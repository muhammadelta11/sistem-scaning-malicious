#!/usr/bin/env python3
"""
Performance Benchmarking Script for SEO Poisoning Detection System

This script benchmarks the performance improvements implemented:
1. Parallel processing for Google queries
2. Enhanced caching with TTL
3. Dynamic keyword loading from database

Usage:
    python performance_benchmark.py [options]

Options:
    --domain DOMAIN       Domain to benchmark (default: test domains)
    --iterations N        Number of benchmark iterations (default: 3)
    --api-key KEY         SerpApi key for testing
    --output FILE         Output file for results (default: benchmark_results.json)
    --verbose             Enable verbose output
"""

import time
import json
import argparse
import logging
import psutil
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import functools
import threading

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import scanner modules
from scanner.core_scanner import perform_verified_scan, search_google
from scanner.data_manager import load_resources
from scanner.config import MALICIOUS_KEYWORDS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Comprehensive performance benchmarking class"""

    def __init__(self, api_key=None, output_file='benchmark_results.json'):
        self.api_key = api_key or os.getenv('SERPAPI_API_KEY')
        self.output_file = output_file
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'benchmarks': []
        }

        # Load resources
        self.model, self.label_mapping, self.ranking_data = load_resources()

        # Test domains for benchmarking
        self.test_domains = [
            'google.com',  # Clean domain
            'github.com',  # Clean domain
            'stackoverflow.com',  # Clean domain
            # Add more test domains as needed
        ]

    def _get_system_info(self):
        """Get system information for benchmarking context"""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_total': psutil.virtual_memory().total,
            'python_version': sys.version,
            'platform': sys.platform
        }

    def _measure_memory_usage(self):
        """Measure current memory usage"""
        process = psutil.Process(os.getpid())
        return {
            'rss': process.memory_info().rss,
            'vms': process.memory_info().vms,
            'percent': process.memory_percent()
        }

    def _time_function(self, func, *args, **kwargs):
        """Time a function execution and measure resources"""
        start_time = time.time()
        start_memory = self._measure_memory_usage()

        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.time()
        end_memory = self._measure_memory_usage()

        return {
            'execution_time': end_time - start_time,
            'memory_start': start_memory,
            'memory_end': end_memory,
            'memory_delta': end_memory['rss'] - start_memory['rss'],
            'success': success,
            'error': error,
            'result': result
        }

    def benchmark_search_google_sequential(self, domain, queries):
        """Benchmark Google search with sequential processing (old method)"""
        all_results = []
        total_api_calls = 0

        for query in queries:
            try:
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": self.api_key,
                    "num": 20
                }

                search = __import__('serpapi.google_search', fromlist=['GoogleSearch']).GoogleSearch(params)
                results = search.get_dict().get('organic_results', [])
                all_results.extend(results)
                total_api_calls += 1

            except Exception as e:
                logger.warning(f"Sequential search failed for query '{query}': {e}")
                continue

        return all_results, total_api_calls

    def benchmark_search_google_parallel(self, domain, queries):
        """Benchmark Google search with parallel processing (new method)"""
        # Import the actual function from core_scanner
        from scanner.core_scanner import search_google

        # Mock fallback key for testing (use same key)
        fallback_key = self.api_key

        # Call the parallel search function
        all_results = search_google(domain, self.api_key, fallback_key)

        # Estimate API calls (4 queries total)
        total_api_calls = len(queries)

        return all_results, total_api_calls

    def benchmark_caching(self, domain, iterations=5):
        """Benchmark caching performance"""
        cache_hits = 0
        cache_misses = 0
        total_time = 0

        # Clear any existing cache
        from scanner.core_scanner import cached_domain_intelligence, cached_deep_analysis
        cached_domain_intelligence.cache_clear()
        cached_deep_analysis.cache_clear()

        # First run - should be cache misses
        logger.info("Running first scan (cache misses)...")
        start_time = time.time()
        result1 = perform_verified_scan(
            domain, self.api_key, self.api_key, "Cepat (Google Only)",
            False, self.model, self.label_mapping, False
        )
        first_run_time = time.time() - start_time

        # Second run - should benefit from caching
        logger.info("Running second scan (cache hits)...")
        start_time = time.time()
        result2 = perform_verified_scan(
            domain, self.api_key, self.api_key, "Cepat (Google Only)",
            False, self.model, self.label_mapping, False
        )
        second_run_time = time.time() - start_time

        # Get cache info
        domain_cache_info = cached_domain_intelligence.cache_info()
        deep_cache_info = cached_deep_analysis.cache_info()

        return {
            'first_run_time': first_run_time,
            'second_run_time': second_run_time,
            'time_improvement': first_run_time - second_run_time,
            'cache_info': {
                'domain_intelligence': {
                    'hits': domain_cache_info.hits,
                    'misses': domain_cache_info.misses,
                    'maxsize': domain_cache_info.maxsize,
                    'currsize': domain_cache_info.currsize
                },
                'deep_analysis': {
                    'hits': deep_cache_info.hits,
                    'misses': deep_cache_info.misses,
                    'maxsize': deep_cache_info.maxsize,
                    'currsize': deep_cache_info.currsize
                }
            }
        }

    def benchmark_keyword_loading(self):
        """Benchmark keyword loading from database vs hardcoded"""
        # Test hardcoded loading
        hardcoded_keywords = MALICIOUS_KEYWORDS

        # Test database loading
        try:
            from scanner.models import MaliciousKeyword
            db_keywords = list(MaliciousKeyword.objects.filter(is_active=True).values_list('keyword', flat=True))
            if not db_keywords:
                db_keywords = hardcoded_keywords  # Fallback
        except:
            db_keywords = hardcoded_keywords

        return {
            'hardcoded_count': len(hardcoded_keywords),
            'database_count': len(db_keywords),
            'keywords_match': set(hardcoded_keywords) == set(db_keywords)
        }

    def run_full_benchmark(self, domains=None, iterations=3):
        """Run complete benchmark suite"""
        if domains is None:
            domains = self.test_domains[:2]  # Use first 2 domains for speed

        logger.info(f"Starting performance benchmark with {len(domains)} domains, {iterations} iterations each")

        benchmark_results = []

        for domain in domains:
            logger.info(f"Benchmarking domain: {domain}")

            domain_results = {
                'domain': domain,
                'timestamp': datetime.now().isoformat(),
                'iterations': []
            }

            for i in range(iterations):
                logger.info(f"Iteration {i+1}/{iterations} for {domain}")

                iteration_result = {
                    'iteration': i + 1,
                    'parallel_processing': {},
                    'caching': {},
                    'keyword_loading': {},
                    'full_scan': {}
                }

                # Benchmark parallel vs sequential processing
                queries = [
                    f'site:{domain} "slot gacor"',
                    f'site:{domain} "judi online"',
                    f'site:{domain} "bokep"',
                    f'site:{domain} "hacked"'
                ]

                # Sequential processing benchmark
                seq_result = self._time_function(
                    self.benchmark_search_google_sequential,
                    domain, queries
                )
                iteration_result['parallel_processing']['sequential'] = seq_result

                # Parallel processing benchmark
                par_result = self._time_function(
                    self.benchmark_search_google_parallel,
                    domain, queries
                )
                iteration_result['parallel_processing']['parallel'] = par_result

                # Caching benchmark
                cache_result = self._time_function(self.benchmark_caching, domain)
                iteration_result['caching'] = cache_result

                # Keyword loading benchmark
                kw_result = self._time_function(self.benchmark_keyword_loading)
                iteration_result['keyword_loading'] = kw_result

                # Full scan benchmark
                full_scan_result = self._time_function(
                    perform_verified_scan,
                    domain, self.api_key, self.api_key, "Cepat (Google Only)",
                    False, self.model, self.label_mapping, False
                )
                iteration_result['full_scan'] = full_scan_result

                domain_results['iterations'].append(iteration_result)

            benchmark_results.append(domain_results)

        self.results['benchmarks'] = benchmark_results
        return self.results

    def generate_report(self):
        """Generate comprehensive benchmark report"""
        if not self.results['benchmarks']:
            return "No benchmark data available"

        report = []
        report.append("# Performance Benchmark Report")
        report.append(f"Generated: {self.results['timestamp']}")
        report.append("")

        report.append("## System Information")
        sys_info = self.results['system_info']
        report.append(f"- CPU Cores: {sys_info['cpu_count']} physical, {sys_info['cpu_count_logical']} logical")
        report.append(f"- Memory: {sys_info['memory_total'] // (1024**3)} GB")
        report.append(f"- Platform: {sys_info['platform']}")
        report.append("")

        for benchmark in self.results['benchmarks']:
            domain = benchmark['domain']
            report.append(f"## Domain: {domain}")
            report.append("")

            # Aggregate results across iterations
            parallel_times = []
            sequential_times = []
            cache_improvements = []
            full_scan_times = []

            for iteration in benchmark['iterations']:
                # Parallel processing comparison
                seq_time = iteration['parallel_processing']['sequential']['execution_time']
                par_time = iteration['parallel_processing']['parallel']['execution_time']
                sequential_times.append(seq_time)
                parallel_times.append(par_time)

                # Caching improvements
                cache_imp = iteration['caching']['result']['time_improvement']
                cache_improvements.append(cache_imp)

                # Full scan times
                full_time = iteration['full_scan']['execution_time']
                full_scan_times.append(full_time)

            # Calculate averages
            avg_seq = sum(sequential_times) / len(sequential_times)
            avg_par = sum(parallel_times) / len(parallel_times)
            avg_cache_imp = sum(cache_improvements) / len(cache_improvements)
            avg_full_scan = sum(full_scan_times) / len(full_scan_times)

            speedup = avg_seq / avg_par if avg_par > 0 else 0

            report.append("### Parallel Processing Performance")
            report.append(".2f"            report.append(".2f"            report.append(".1f"            report.append("")

            report.append("### Caching Performance")
            report.append(".2f"            report.append("")

            report.append("### Full Scan Performance")
            report.append(".2f"            report.append("")

            # Cache statistics
            if benchmark['iterations']:
                cache_info = benchmark['iterations'][0]['caching']['result']['cache_info']
                report.append("### Cache Statistics")
                report.append(f"- Domain Intelligence Cache: {cache_info['domain_intelligence']['hits']} hits, {cache_info['domain_intelligence']['misses']} misses")
                report.append(f"- Deep Analysis Cache: {cache_info['deep_analysis']['hits']} hits, {cache_info['deep_analysis']['misses']} misses")
                report.append("")

        return "\n".join(report)

    def save_results(self):
        """Save benchmark results to file"""
        with open(self.output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"Results saved to {self.output_file}")

def main():
    parser = argparse.ArgumentParser(description='Performance Benchmark for SEO Poisoning Detection')
    parser.add_argument('--domain', nargs='+', help='Domains to benchmark')
    parser.add_argument('--iterations', type=int, default=3, help='Number of iterations per domain')
    parser.add_argument('--api-key', help='SerpApi key (or set SERPAPI_API_KEY env var)')
    parser.add_argument('--output', default='benchmark_results.json', help='Output file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--report-only', action='store_true', help='Generate report from existing results')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    benchmark = PerformanceBenchmark(args.api_key, args.output)

    if args.report_only:
        # Load existing results and generate report
        try:
            with open(args.output, 'r') as f:
                benchmark.results = json.load(f)
        except FileNotFoundError:
            logger.error(f"Results file {args.output} not found")
            return

        report = benchmark.generate_report()
        print(report)
        return

    # Run benchmark
    results = benchmark.run_full_benchmark(args.domain, args.iterations)
    benchmark.save_results()

    # Generate and display report
    report = benchmark.generate_report()
    print("\n" + "="*80)
    print(report)
    print("="*80)

    # Save report to file
    report_file = args.output.replace('.json', '_report.md')
    with open(report_file, 'w') as f:
        f.write(report)
    logger.info(f"Report saved to {report_file}")

if __name__ == '__main__':
    main()

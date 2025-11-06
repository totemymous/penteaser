"""
Browser automation wrapper for Playwright/Selenium.

This module provides a unified interface for browser automation
with support for headful mode, session recording, and human-in-the-loop.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .config import BROWSER_TYPE, HEADFUL_MODE, BROWSER_TIMEOUT, SESSION_RECORDINGS_PATH

logger = logging.getLogger(__name__)


class BrowserSession:
    """
    Browser automation session with recording capabilities.

    This class wraps Playwright or Selenium to provide:
    - Headful browser mode for transparency
    - Session metadata recording (DOM snapshots, screenshots)
    - Human-in-the-loop pause/resume
    """

    def __init__(self, session_id: int, target_url: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize browser session.

        Args:
            session_id: Database session ID
            target_url: Target URL to test
            config: Optional browser configuration
        """
        self.session_id = session_id
        self.target_url = target_url
        self.config = config or {}
        self.browser = None
        self.page = None
        self.context = None
        self.recording_path = Path(SESSION_RECORDINGS_PATH) / f"session_{session_id}"
        self.screenshot_count = 0
        self.interaction_count = 0

        logger.info(f"Initialized browser session {session_id} for {target_url}")

    async def start(self):
        """
        Start browser and navigate to target.

        Launches browser in headful mode (if configured) and navigates to target URL.
        """
        logger.info(f"Starting browser (type: {BROWSER_TYPE}, headful: {HEADFUL_MODE})")

        if BROWSER_TYPE == "playwright":
            await self._start_playwright()
        elif BROWSER_TYPE == "selenium":
            self._start_selenium()
        else:
            raise ValueError(f"Unsupported browser type: {BROWSER_TYPE}")

        # Create recording directory
        self.recording_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Recording session to: {self.recording_path}")

    async def _start_playwright(self):
        """Start Playwright browser session"""
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(
            headless=not HEADFUL_MODE,
            timeout=BROWSER_TIMEOUT,
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(self.recording_path) if HEADFUL_MODE else None,
        )
        self.page = await self.context.new_page()

        logger.info(f"Navigating to {self.target_url}")
        await self.page.goto(self.target_url, timeout=BROWSER_TIMEOUT)

    def _start_selenium(self):
        """Start Selenium browser session"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        if not HEADFUL_MODE:
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")

        self.browser = webdriver.Chrome(options=options)
        self.page = self.browser  # In Selenium, driver acts as page

        logger.info(f"Navigating to {self.target_url}")
        self.browser.get(self.target_url)

    async def analyze_dom(self) -> Dict[str, Any]:
        """
        Perform passive DOM analysis without payload injection.

        Returns:
            Dictionary with DOM metadata (forms, inputs, suspicious patterns)
        """
        logger.info("Analyzing DOM structure...")

        if BROWSER_TYPE == "playwright":
            # Find all forms and inputs
            forms = await self.page.query_selector_all("form")
            inputs = await self.page.query_selector_all("input, textarea")

            metadata = {
                "form_count": len(forms),
                "input_count": len(inputs),
                "url": self.page.url,
                "title": await self.page.title(),
            }

            # Identify potentially vulnerable inputs (no payload testing)
            vulnerable_inputs = []
            for input_elem in inputs:
                input_type = await input_elem.get_attribute("type")
                input_name = await input_elem.get_attribute("name")

                # Flag text inputs without obvious sanitization attributes
                if input_type in ["text", "search", None]:
                    vulnerable_inputs.append({
                        "name": input_name,
                        "type": input_type,
                        "reason": "text_input_without_sanitization_check"
                    })

            metadata["suspicious_inputs"] = vulnerable_inputs
            metadata["analysis_type"] = "passive_dom_fingerprint"

            logger.info(f"Found {len(vulnerable_inputs)} potentially interesting inputs")
            return metadata

        elif BROWSER_TYPE == "selenium":
            # Similar analysis with Selenium
            forms = self.browser.find_elements("tag name", "form")
            inputs = self.browser.find_elements("tag name", "input")

            return {
                "form_count": len(forms),
                "input_count": len(inputs),
                "url": self.browser.current_url,
                "title": self.browser.title,
                "analysis_type": "passive_dom_fingerprint"
            }

    async def take_screenshot(self, name: str = "screenshot") -> str:
        """
        Capture screenshot for evidence.

        Args:
            name: Screenshot filename prefix

        Returns:
            Path to screenshot file
        """
        self.screenshot_count += 1
        screenshot_path = self.recording_path / f"{name}_{self.screenshot_count}.png"

        if BROWSER_TYPE == "playwright":
            await self.page.screenshot(path=str(screenshot_path))
        elif BROWSER_TYPE == "selenium":
            self.browser.save_screenshot(str(screenshot_path))

        logger.info(f"Screenshot saved: {screenshot_path}")
        return str(screenshot_path)

    async def wait_for_approval(self) -> bool:
        """
        Pause and wait for human approval.

        In real implementation, this would:
        1. Update session status to PENDING_APPROVAL in database
        2. Poll database or listen to Redis pub/sub for approval
        3. Return True if approved, False if rejected

        Returns:
            True if approved, False if rejected
        """
        logger.warning("Session requires human approval - waiting...")
        logger.info("In real implementation: update DB status and wait for user decision")

        # Placeholder: In real implementation, poll database or Redis
        # For now, just return True (auto-approve in scaffold)
        return True

    async def close(self):
        """Close browser and cleanup resources"""
        logger.info("Closing browser session...")

        if BROWSER_TYPE == "playwright" and self.browser:
            await self.context.close()
            await self.browser.close()
            await self._playwright.stop()
        elif BROWSER_TYPE == "selenium" and self.browser:
            self.browser.quit()

        logger.info(f"Session {self.session_id} closed. Screenshots: {self.screenshot_count}")

    def get_session_metadata(self) -> Dict[str, Any]:
        """
        Get session recording metadata.

        Returns:
            Dictionary with session statistics
        """
        return {
            "session_id": self.session_id,
            "recording_path": str(self.recording_path),
            "screenshot_count": self.screenshot_count,
            "interaction_count": self.interaction_count,
        }

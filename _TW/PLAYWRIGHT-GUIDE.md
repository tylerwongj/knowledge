# Playwright Guide - Complete Reference

## What is Playwright?
Playwright is a web automation tool that opens real browsers (Chrome, Firefox, Safari) and controls them programmatically. It can click buttons, fill forms, take screenshots, navigate pages, and automate any web interaction you can do manually.

## Key Commands

### Running Tests
```bash
# Run all tests (headless - no visible browser)
==npx playwright test==

# Run all tests with visible browser windows (but fast)
npx playwright test --headed

# Run specific test file
npx playwright test tests/01-basic-navigation.spec.js

# Run specific test by name
npx playwright test --grep "navigate and take screenshot"

# Run only Chrome browser
npx playwright test --project=chromium
```

### Best Ways to See Browser Actions
```bash
# Debug mode - pauses at each step, browser stays open
npx playwright test tests/01-basic-navigation.spec.js --debug --grep "navigate and take screenshot"

# UI mode - interactive interface with full control
npx playwright test --ui

# Note: --headed runs too fast to see, debug/UI modes are better
```

### Reports & Browser Management
```bash
# Show HTML test report
npx playwright show-report

# Install browsers (if needed)
npx playwright install
```

## Test Structure

### ==Basic Test Anatomy==
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Test Group Name', () => {
  test('individual test name', async ({ page }) => {
    // Your test code here
    await page.goto('https://example.com');
    await page.click('button');
    await expect(page).toHaveTitle('Expected Title');
  });
});
```

### Key Components
- `test.describe()` - Groups related tests together
- `test()` - Individual test cases with descriptive names
- `{ page }` - Browser page object (most common)
- `{ context }` - Browser context for multiple pages/tabs
- `{ browser }` - Browser instance for advanced scenarios

## Common Page Actions

### Navigation
```javascript
await page.goto('https://example.com');
await page.goBack();
await page.goForward();
await page.reload();
```

### Element Interaction
```javascript
await page.click('button');
await page.click('text=Click Me');
await page.fill('input[name="email"]', 'test@example.com');
await page.selectOption('select', 'option-value');
```

### Waiting & Verification
```javascript
await page.waitForSelector('h1');
await page.waitForLoadState('networkidle');
await expect(page).toHaveTitle('Expected Title');
await expect(page.locator('h1')).toContainText('Welcome');
```

### Screenshots & Media
```javascript
await page.screenshot({ path: 'screenshot.png' });
await page.screenshot({ path: 'full-page.png', fullPage: true });
```

### Finding Elements
```javascript
const button = page.locator('button');
const heading = page.locator('h1');
const byText = page.locator('text=Click Me');
const byTestId = page.locator('[data-testid="submit"]');
```

## Example Test Breakdown
```javascript
test('navigate and take screenshot', async ({ page }) => {
  // 1. Navigate to website
  await page.goto('https://playwright.dev');
  
  // 2. Take a screenshot
  await page.screenshot({ path: 'playwright-homepage.png' });
  
  // 3. Verify page content
  await expect(page.locator('h1')).toContainText('Playwright');
});
```

This test:
1. Opens a browser
2. Goes to playwright.dev
3. Takes a screenshot and saves it
4. Checks that the h1 tag contains "Playwright"

## Project Configuration
The `playwright.config.js` file controls:
- Which browsers to test (Chrome, Firefox, Safari, mobile)
- Test settings (screenshots, videos, retries)
- Base URLs and timeouts

## Tips for Learning
1. Start with `npx playwright test --ui` - best way to see what's happening
2. Use `--debug` to step through tests line by line
3. The `--headed` flag shows browsers but they run too fast to see
4. Screenshots are automatically saved to help debug failures
5. Each test runs in a fresh browser context (clean slate)

## This Project's Test Files
- `01-basic-navigation.spec.js` - Navigate, screenshots, back/forward
- `02-form-interactions.spec.js` - Fill forms, submit data  
- `03-element-interactions.spec.js` - Click buttons, interact with elements
- `04-waiting-strategies.spec.js` - Wait for elements, network, timeouts
- `05-screenshots-videos.spec.js` - Capture media and visual testing
- `06-advanced-patterns.spec.js` - Complex automation patterns

## Key Takeaways
- Playwright automates real browsers, not fake ones
- Tests are written in JavaScript using async/await
- The `page` object is your main tool for browser interaction
- `--debug` and `--ui` modes are essential for learning and debugging
- Each test starts with a clean browser state
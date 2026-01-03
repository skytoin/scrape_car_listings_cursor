"""
Debug script to analyze image extraction from a specific listing page.
This will help us understand the page structure and fix the image extraction.
"""

import asyncio

from playwright.async_api import async_playwright


async def debug_page_structure(url: str) -> None:
    """
    Analyze the page structure to understand how to extract gallery images.

    Args:
        url: URL of the listing page to analyze
    """
    print(f"Analyzing page: {url}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)  # Wait for images to load

        # 1. Check for gallery containers
        print("=" * 60)
        print("1. SEARCHING FOR GALLERY CONTAINERS")
        print("=" * 60)

        gallery_selectors = [
            'div[class*="media-gallery"]',
            'section[class*="media-gallery"]',
            'div[data-testid="media-gallery"]',
            'div[class*="vehicle-photos"]',
            'div[class*="photo-gallery"]',
            'div[class*="gallery"]',
            '[class*="VehiclePhotos"]',
            '[class*="ImageGallery"]',
        ]

        found_container = False
        for selector in gallery_selectors:
            element = await page.query_selector(selector)
            if element:
                print(f"✅ FOUND: {selector}")
                # Get the class name
                class_name = await element.get_attribute("class")
                print(f"   Class: {class_name}")
                found_container = True
                break
            else:
                print(f"❌ Not found: {selector}")

        if not found_container:
            print("\n⚠️  No gallery container found with predefined selectors")

        # 2. Find all images with cstatic-images.com
        print("\n" + "=" * 60)
        print("2. ALL IMAGES FROM cstatic-images.com")
        print("=" * 60)

        all_images = await page.query_selector_all("img")
        cstatic_images = []

        for img in all_images:
            src = await img.get_attribute("src")
            data_src = await img.get_attribute("data-src")
            url = src or data_src

            if url and "cstatic-images.com" in url:
                # Get parent info
                parent_class = await page.evaluate(
                    "(img) => img.parentElement?.className || ''", img
                )
                cstatic_images.append(
                    {"url": url, "parent_class": parent_class[:50]}
                )

        print(f"Total cstatic-images found: {len(cstatic_images)}\n")
        for idx, img_info in enumerate(cstatic_images, 1):
            print(f"{idx}. URL: {img_info['url'][:80]}...")
            print(f"   Parent class: {img_info['parent_class']}\n")

        # 3. Try to find the actual gallery using JavaScript
        print("=" * 60)
        print("3. ANALYZING PAGE STRUCTURE WITH JAVASCRIPT")
        print("=" * 60)

        gallery_info = await page.evaluate(
            """() => {
            // Look for common gallery patterns
            const galleries = [];

            // Method 1: Find by common class names
            const commonClasses = ['gallery', 'photos', 'media', 'carousel', 'slideshow'];
            commonClasses.forEach(cls => {
                const elements = document.querySelectorAll(`[class*="${cls}" i]`);
                elements.forEach(el => {
                    const images = el.querySelectorAll('img');
                    const cstaticImages = Array.from(images).filter(img =>
                        (img.src || img.dataset.src || '').includes('cstatic-images.com')
                    );
                    if (cstaticImages.length > 0) {
                        galleries.push({
                            selector: el.className,
                            imageCount: cstaticImages.length,
                            firstImageUrl: (cstaticImages[0].src || cstaticImages[0].dataset.src || '').substring(0, 80)
                        });
                    }
                });
            });

            return galleries;
        }"""
        )

        if gallery_info:
            print(f"Found {len(gallery_info)} potential gallery containers:\n")
            for idx, info in enumerate(gallery_info, 1):
                print(f"{idx}. Selector: {info['selector'][:60]}")
                print(f"   Images: {info['imageCount']}")
                print(f"   First image: {info['firstImageUrl']}...\n")
        else:
            print("No gallery containers found\n")

        # 4. Check for picture elements
        print("=" * 60)
        print("4. CHECKING PICTURE ELEMENTS")
        print("=" * 60)

        pictures = await page.query_selector_all("picture")
        picture_count = 0
        for pic in pictures:
            imgs = await pic.query_selector_all("img")
            for img in imgs:
                src = await img.get_attribute("src")
                if src and "cstatic-images.com" in src:
                    picture_count += 1
                    if picture_count <= 5:  # Show first 5
                        print(f"{picture_count}. {src[:80]}...")

        print(f"\nTotal picture elements with cstatic images: {picture_count}")

        # 5. Get page HTML snippet for manual inspection
        print("\n" + "=" * 60)
        print("5. SAVING PAGE HTML FOR INSPECTION")
        print("=" * 60)

        html = await page.content()
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Saved full page HTML to: debug_page.html")
        print("   You can inspect this file to see the exact structure\n")

        await browser.close()


async def main() -> None:
    """Run the debug analysis."""
    # The example URL from the user
    url = "https://www.cars.com/vehicledetail/8492ded5-80af-44d1-b027-cbb2b4ec897d/"

    print("🔍 DEBUG: Image Extraction Analysis\n")
    await debug_page_structure(url)
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    asyncio.run(main())

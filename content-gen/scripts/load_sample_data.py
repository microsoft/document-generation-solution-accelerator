"""
Sample data loader for Content Generation Solution Accelerator.

This script loads sample product data into CosmosDB for testing and demos.
"""

import asyncio
import json
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.services.cosmos_service import get_cosmos_service
from backend.models import Product


SAMPLE_PRODUCTS = [
    {
        "product_name": "ProMax Wireless Headphones",
        "category": "Electronics",
        "sub_category": "Audio",
        "marketing_description": "Immerse yourself in crystal-clear sound with our flagship wireless headphones featuring industry-leading noise cancellation.",
        "detailed_spec_description": "40mm custom-designed drivers deliver rich, balanced audio. Advanced Active Noise Cancellation blocks outside noise. 30-hour battery life with quick charge (10 min = 5 hours). Bluetooth 5.2 with multipoint connection. Premium memory foam ear cushions. Foldable design with travel case included.",
        "sku": "PM-WH-2024-001",
        "model": "ProMax-Elite",
        "image_description": "Sleek over-ear headphones in premium matte black finish with rose gold accent rings around the ear cups. Features thick memory foam cushions covered in breathable protein leather. Adjustable stainless steel headband with soft padding. Touch controls visible on the right ear cup."
    },
    {
        "product_name": "UltraFit Wireless Earbuds",
        "category": "Electronics",
        "sub_category": "Audio",
        "marketing_description": "Stay active with earbuds designed for movement. Secure fit, powerful sound, all-day comfort.",
        "detailed_spec_description": "10mm dynamic drivers with deep bass. IPX5 water and sweat resistant. 8 hours playback, 32 hours with case. Touch controls and voice assistant support. Wireless charging compatible. Three sizes of silicone and foam tips included.",
        "sku": "UF-EB-2024-002",
        "model": "UltraFit-Pro",
        "image_description": "Compact true wireless earbuds in pearl white with a sleek charging case. Earbuds feature an ergonomic wingtip design for secure fit. The case has a matte finish with LED indicator lights and USB-C port visible on the bottom."
    },
    {
        "product_name": "SmartHome Hub Pro",
        "category": "Electronics",
        "sub_category": "Smart Home",
        "marketing_description": "Control your entire smart home from one elegant hub. Voice control, automation, and seamless integration.",
        "detailed_spec_description": "7-inch HD touchscreen display. Built-in premium speakers with 360° sound. Works with Alexa, Google Assistant, and HomeKit. Zigbee and Z-Wave built-in. Matter compatible. Privacy shutter for camera. Wall mount or tabletop stand included.",
        "sku": "SH-HUB-2024-003",
        "model": "SmartHub-7",
        "image_description": "Modern smart home hub with a 7-inch display showing a home dashboard. Sleek charcoal gray frame with fabric-covered speaker grille at the bottom. Sits on a minimalist aluminum stand. The screen displays room controls and weather widgets."
    },
    {
        "product_name": "AeroLight Running Shoes",
        "category": "Footwear",
        "sub_category": "Athletic",
        "marketing_description": "Engineered for speed. Our lightest running shoe ever delivers responsive cushioning and breathable comfort.",
        "detailed_spec_description": "Weight: 7.2 oz (men's size 9). Nitrogen-infused foam midsole for 15% more energy return. Engineered mesh upper with targeted ventilation zones. Carbon fiber plate for propulsion. Rubber outsole with multi-directional traction pattern. Reflective elements for visibility.",
        "sku": "AL-RUN-2024-004",
        "model": "AeroLight-X",
        "image_description": "Dynamic running shoe in electric blue with neon green accents. Features a lightweight mesh upper with visible ventilation holes. The midsole shows a distinctive curved carbon plate design. Translucent rubber outsole reveals the foam construction beneath."
    },
    {
        "product_name": "Executive Leather Briefcase",
        "category": "Accessories",
        "sub_category": "Bags",
        "marketing_description": "Timeless elegance meets modern functionality. Handcrafted from premium full-grain leather.",
        "detailed_spec_description": "Full-grain vegetable-tanned leather. Padded compartment fits laptops up to 15.6 inches. Organizer pocket with RFID-blocking liner. YKK zippers with custom-designed pulls. Adjustable, removable shoulder strap. Dimensions: 16\" x 12\" x 4\". Dust bag included.",
        "sku": "EL-BRIEF-2024-005",
        "model": "Executive-Classic",
        "image_description": "Sophisticated brown leather briefcase with rich patina and subtle grain texture. Features brass-toned hardware and buckle closures. Front pocket with a sleek zipper. Top carry handles are reinforced with stitching. The leather shows natural variations indicating genuine premium quality."
    },
    {
        "product_name": "Ceramic Pour-Over Coffee Maker",
        "category": "Home & Kitchen",
        "sub_category": "Coffee",
        "marketing_description": "Artisan coffee at home. Handmade ceramic dripper delivers a perfectly balanced, flavorful cup every time.",
        "detailed_spec_description": "Handcrafted ceramic with food-safe glaze. Unique spiral ridges for optimal extraction. Fits standard #2 paper filters. Serves 1-2 cups. Dishwasher safe. Heat resistant cork sleeve. Includes 30 unbleached paper filters.",
        "sku": "CP-COFFEE-2024-006",
        "model": "ArtisanBrew",
        "image_description": "Elegant ceramic pour-over coffee dripper in creamy white with subtle blue-gray spiral ridges inside. Sits on a natural cork base. The ceramic has a smooth, hand-finished quality with a gentle sheen. A glass carafe is positioned beneath to catch the brew."
    },
    {
        "product_name": "Performance Yoga Mat",
        "category": "Sports & Fitness",
        "sub_category": "Yoga",
        "marketing_description": "Elevate your practice. Superior grip, cushioning, and eco-friendly materials for yogis who demand the best.",
        "detailed_spec_description": "6mm thick natural rubber with microfiber surface. Dimensions: 72\" x 26\". Non-slip grip improves with moisture. Alignment markers laser-etched. Antimicrobial treatment. Free from PVC, latex, and toxic materials. Includes cotton carrying strap.",
        "sku": "PY-MAT-2024-007",
        "model": "ZenGrip-Pro",
        "image_description": "Premium yoga mat rolled partially open, showing a deep forest green surface with subtle alignment lines. The underside visible at the roll shows a natural rubber texture in black. A cotton strap in matching green wraps around the rolled mat."
    },
    {
        "product_name": "Titanium Travel Watch",
        "category": "Accessories",
        "sub_category": "Watches",
        "marketing_description": "Adventure-ready timekeeping. Lightweight titanium construction with world-class precision.",
        "detailed_spec_description": "Grade 2 titanium case, 42mm diameter. Swiss automatic movement with 72-hour power reserve. Sapphire crystal with anti-reflective coating. Water resistant to 200 meters. Dual time zone display. Interchangeable NATO and titanium bracelet included.",
        "sku": "TT-WATCH-2024-008",
        "model": "Explorer-Ti",
        "image_description": "Rugged titanium watch with a brushed silver-gray case showing subtle tool marks from the finishing process. Black dial with luminescent hands and hour markers. A rotating bezel with minute markings surrounds the sapphire crystal. The watch is shown on a gray NATO strap."
    },
    {
        "product_name": "Organic Cotton Bedding Set",
        "category": "Home & Living",
        "sub_category": "Bedding",
        "marketing_description": "Sleep in sustainable luxury. GOTS-certified organic cotton that gets softer with every wash.",
        "detailed_spec_description": "100% GOTS-certified organic cotton, 400 thread count sateen weave. Set includes: 1 duvet cover, 2 pillowcases. Available in Queen and King sizes. Hidden button closure. Oeko-Tex certified for safety. Pre-washed for extra softness. Machine washable.",
        "sku": "OC-BED-2024-009",
        "model": "PureRest-Sateen",
        "image_description": "Luxurious bedding set displayed on a neatly made bed. The soft white cotton has a subtle sheen characteristic of sateen weave. Crisp, clean lines with perfectly tucked corners. The pillowcases feature a simple envelope closure. Natural light highlights the fabric's smooth texture."
    },
    {
        "product_name": "Smart Fitness Tracker",
        "category": "Electronics",
        "sub_category": "Wearables",
        "marketing_description": "Your health companion. Advanced sensors, beautiful display, and insights that help you live better.",
        "detailed_spec_description": "1.4\" AMOLED display, always-on option. Heart rate, SpO2, stress, and sleep monitoring. Built-in GPS and 20+ sport modes. 7-day battery life. 5 ATM water resistance. Contactless payments. Compatible with iOS and Android.",
        "sku": "SF-TRACK-2024-010",
        "model": "VitalBand-Pro",
        "image_description": "Sleek fitness tracker with a curved rectangular display showing colorful health metrics. The case is polished black aluminum with a subtle graphite tone. Attached is a soft silicone band in midnight blue with a secure buckle clasp. The screen displays heart rate, steps, and time."
    }
]


async def load_sample_data():
    """Load sample products into CosmosDB."""
    print("Loading sample product data...")
    
    cosmos_service = await get_cosmos_service()
    
    for product_data in SAMPLE_PRODUCTS:
        try:
            product = Product(**product_data)
            await cosmos_service.upsert_product(product)
            print(f"  ✓ Loaded: {product.product_name} ({product.sku})")
        except Exception as e:
            print(f"  ✗ Failed to load {product_data.get('product_name', 'unknown')}: {e}")
    
    print(f"\nLoaded {len(SAMPLE_PRODUCTS)} sample products.")


async def main():
    """Main entry point."""
    try:
        await load_sample_data()
    except Exception as e:
        print(f"Error loading sample data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

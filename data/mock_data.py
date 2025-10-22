"""Mock data for the customer care system demo."""

from datetime import datetime, timedelta
from typing import Dict, List, Any

# Mock orders data
orders: Dict[str, Dict[str, Any]] = {
    "12345": {
        "customer": "Sarah Miller",
        "customer_email": "sarah.miller@email.com",
        "product": "TechBook Pro 15",
        "product_id": "TB-PRO-15",
        "price": 1299.99,
        "order_date": "2024-01-28",
        "delivery_date": "2024-01-30",
        "status": "delivered",
        "warranty": "2 years",
        "warranty_expires": "2026-01-30",
        "purchase_location": "online"
    },
    "12346": {
        "customer": "John Davis",
        "customer_email": "john.davis@email.com",
        "product": "TechBook Air 13",
        "product_id": "TB-AIR-13",
        "price": 899.99,
        "order_date": "2024-02-15",
        "delivery_date": "2024-02-18",
        "status": "delivered",
        "warranty": "1 year",
        "warranty_expires": "2025-02-18",
        "purchase_location": "online"
    },
    "12347": {
        "customer": "Emily Wilson",
        "customer_email": "emily.wilson@email.com",
        "product": "TechBook Gaming 17",
        "product_id": "TB-GAME-17",
        "price": 1899.99,
        "order_date": "2024-03-01",
        "delivery_date": "2024-03-05",
        "status": "shipped",
        "warranty": "3 years",
        "warranty_expires": "2027-03-05",
        "purchase_location": "store"
    }
}

# Mock products data
products: Dict[str, Dict[str, Any]] = {
    "TB-PRO-15": {
        "name": "TechBook Pro 15",
        "specs": {
            "ram": "16GB DDR4",
            "storage": "512GB SSD",
            "processor": "Intel i7-12700H",
            "graphics": "Intel Iris Xe",
            "display": "15.6\" 1920x1080 IPS",
            "battery": "8 hours",
            "weight": "3.5 lbs"
        },
        "price": 1299.99,
        "inventory": 45,
        "rating": 4.5,
        "category": "professional",
        "warranty_period": "2 years"
    },
    "TB-AIR-13": {
        "name": "TechBook Air 13",
        "specs": {
            "ram": "8GB DDR4",
            "storage": "256GB SSD",
            "processor": "Intel i5-1235U",
            "graphics": "Intel Iris Xe",
            "display": "13.3\" 1920x1080 IPS",
            "battery": "12 hours",
            "weight": "2.8 lbs"
        },
        "price": 899.99,
        "inventory": 122,
        "rating": 4.3,
        "category": "ultrabook",
        "warranty_period": "1 year"
    },
    "TB-GAME-17": {
        "name": "TechBook Gaming 17",
        "specs": {
            "ram": "32GB DDR4",
            "storage": "1TB SSD",
            "processor": "Intel i9-12900H",
            "graphics": "NVIDIA RTX 4060",
            "display": "17.3\" 2560x1440 165Hz",
            "battery": "4 hours",
            "weight": "5.2 lbs"
        },
        "price": 1899.99,
        "inventory": 23,
        "rating": 4.7,
        "category": "gaming",
        "warranty_period": "3 years"
    },
    "TB-BASIC-14": {
        "name": "TechBook Basic 14",
        "specs": {
            "ram": "8GB DDR4",
            "storage": "256GB SSD",
            "processor": "Intel i3-1215U",
            "graphics": "Intel UHD",
            "display": "14\" 1366x768 TN",
            "battery": "10 hours",
            "weight": "3.1 lbs"
        },
        "price": 599.99,
        "inventory": 87,
        "rating": 3.9,
        "category": "budget",
        "warranty_period": "1 year"
    }
}

# Mock knowledge base
knowledge_base: Dict[str, List[str]] = {
    "laptop_wont_turn_on": [
        "Check if the power adapter is properly connected to both the laptop and wall outlet",
        "Try holding the power button for 10-15 seconds to perform a hard reset",
        "Remove the battery (if removable) and reinsert it firmly",
        "Check for LED indicators on the power adapter and laptop",
        "Try a different power outlet",
        "If still not working, the power adapter or internal components may need service"
    ],
    "laptop_overheating": [
        "Ensure all air vents are clear of dust and debris",
        "Use compressed air to clean vents and fan areas",
        "Check that the laptop is on a hard, flat surface for proper airflow",
        "Close unnecessary programs to reduce CPU load",
        "Consider using a laptop cooling pad",
        "Check Task Manager for high CPU usage applications"
    ],
    "slow_performance": [
        "Restart the laptop to clear temporary files and processes",
        "Check available storage space - ensure at least 15% free space",
        "Run disk cleanup to remove temporary files",
        "Check for malware using Windows Defender or antivirus software",
        "Update device drivers and operating system",
        "Consider upgrading RAM if usage consistently exceeds 80%"
    ],
    "wifi_issues": [
        "Restart your router and modem",
        "Forget and reconnect to the WiFi network",
        "Update WiFi adapter drivers",
        "Run Windows Network Troubleshooter",
        "Check if other devices can connect to the same network",
        "Reset network settings if other steps don't work"
    ],
    "screen_issues": [
        "Check display brightness settings",
        "Try connecting an external monitor to isolate the issue",
        "Update display drivers",
        "Check cable connections if using external monitor",
        "Restart in safe mode to test display functionality",
        "If built-in display has physical damage, professional repair needed"
    ]
}

# Company policies
policies: Dict[str, Dict[str, Any]] = {
    "return": {
        "period_days": 30,
        "condition": "Items must be in original condition with all accessories",
        "restocking_fee": 0.15,
        "free_return_reasons": ["defective", "wrong_item", "damaged_shipping"],
        "process": [
            "Contact customer service to initiate return",
            "Receive return authorization number",
            "Package item securely with return label",
            "Drop off at shipping location or schedule pickup"
        ]
    },
    "warranty": {
        "coverage": {
            "1_year": ["manufacturing defects", "hardware failures"],
            "2_year": ["manufacturing defects", "hardware failures", "screen defects"],
            "3_year": ["manufacturing defects", "hardware failures", "screen defects", "accidental damage"]
        },
        "exclusions": ["water damage", "user-caused physical damage", "software issues"],
        "process": [
            "Verify warranty status with order number",
            "Describe the issue in detail",
            "Perform basic troubleshooting steps",
            "If unresolved, arrange for repair or replacement"
        ]
    },
    "exchange": {
        "period_days": 15,
        "eligible_reasons": ["size_issue", "performance_needs", "compatibility"],
        "fee": 50.0,
        "restrictions": ["same_category_only", "price_difference_applies"]
    }
}

def get_order(order_id: str) -> Dict[str, Any]:
    """Retrieve order information by order ID."""
    return orders.get(order_id)

def get_product(product_id: str) -> Dict[str, Any]:
    """Retrieve product information by product ID."""
    return products.get(product_id)

def get_all_products() -> Dict[str, Dict[str, Any]]:
    """Get all products."""
    return products

def search_knowledge_base(query: str) -> List[str]:
    """Search knowledge base for troubleshooting steps."""
    query_lower = query.lower()
    
    # Simple keyword matching
    for issue, steps in knowledge_base.items():
        if any(keyword in query_lower for keyword in issue.split('_')):
            return steps
    
    return []

def get_policy(policy_type: str) -> Dict[str, Any]:
    """Get company policy information."""
    return policies.get(policy_type)
plans_data = [
    {
        "id": 0,
        "name": "Entry Plan",
        "price": "$20/month",
        "amount": 100,  # En centavos
        "stripe_plan_id": "STRIPE_ID_ENTRY",
        "features": [
                "Basic analytics (e.g., conversations, user engagement)",
                "Limited customization options",
                "24/7 Chat Support",
                "Pre-designed conversation flows",
                "Data collection (up to a fixed number, e.g., 500 conversations)"
            ],
        "target_market": ["Small businesses", "Individuals running personal brands"],
        "paypal_plan_id": "P-1WY87893FH282035MMUNQHIQ",
        
    },
    {
        "id": 1,
        "name": "Premium Plan",
        "price": "$100/month",
        "amount": 10000,
        "stripe_plan_id": "STRIPE_ID_PREMIUM",
        "features": [
                "Advanced analytics with customer insights",
                "Complete customization",
                "24/7 Priority Support",
                "API integrations",
                "Unlimited data collection",
                "A/B Testing for conversation flows"
            ],
        "target_market": ["Medium enterprises", "E-commerce platforms"],
        "paypal_plan_id": "P-2JM49794N1364952JMUNQUFQ",
        
    },
    {
        "id": 2,
        "name": "Enterprise Plan",
        "price": "Request a Quote",
        "amount": 5000,
        "stripe_plan_id": "STRIPE_ID_ENTERPRISE",
        "features": [
                "Tailor-made solutions",
                "Dedicated account manager",
                "Multi-domain support"
            ],
        "target_market": [],
        "paypal_plan_id": "P-67N466274H332335LMUNQVQQ",
    }
]

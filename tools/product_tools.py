"""Product management and comparison tools."""

import logging
from typing import Dict, Any, List, Optional
from data.mock_data import get_product, get_all_products

logger = logging.getLogger(__name__)

class ProductTools:
    """Tools for product information and comparison."""
    
    async def get_product_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed product information."""
        try:
            product = get_product(product_id)
            if not product:
                return None
            
            # Add calculated fields
            product_info = product.copy()
            product_info["availability_status"] = self._get_availability_status(product["inventory"])
            product_info["price_tier"] = self._classify_price_tier(product["price"])
            
            logger.info(f"Retrieved product info for {product_id}")
            return product_info
            
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {e}")
            return None
    
    async def compare_products(self, product_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple products side by side."""
        try:
            products = {}
            
            for product_id in product_ids:
                product = get_product(product_id)
                if product:
                    products[product_id] = product
            
            if not products:
                return {"error": "No valid products found for comparison"}
            
            # Generate comparison
            comparison = {
                "products": products,
                "comparison_matrix": self._create_comparison_matrix(products),
                "recommendations": self._generate_recommendations(products)
            }
            
            logger.info(f"Compared products: {list(products.keys())}")
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing products: {e}")
            return {"error": str(e)}
    
    async def check_inventory(self, product_id: str) -> Dict[str, Any]:
        """Check product inventory and availability."""
        try:
            product = get_product(product_id)
            if not product:
                return {"error": "Product not found"}
            
            inventory_info = {
                "product_id": product_id,
                "product_name": product["name"],
                "current_stock": product["inventory"],
                "availability_status": self._get_availability_status(product["inventory"]),
                "estimated_restock": self._estimate_restock(product["inventory"]),
                "backorder_available": product["inventory"] < 10
            }
            
            logger.info(f"Checked inventory for {product_id}: {product['inventory']} units")
            return inventory_info
            
        except Exception as e:
            logger.error(f"Error checking inventory for {product_id}: {e}")
            return {"error": str(e)}
    
    async def get_alternatives(self, product_id: str, criteria: str = "similar_specs") -> List[Dict[str, Any]]:
        """Find alternative products based on criteria."""
        try:
            target_product = get_product(product_id)
            if not target_product:
                return []
            
            all_products = get_all_products()
            alternatives = []
            
            for pid, product in all_products.items():
                if pid == product_id:
                    continue
                
                similarity_score = self._calculate_similarity(target_product, product, criteria)
                if similarity_score > 0.3:  # Threshold for relevance
                    alt_product = product.copy()
                    alt_product["product_id"] = pid
                    alt_product["similarity_score"] = similarity_score
                    alt_product["key_differences"] = self._identify_differences(target_product, product)
                    alternatives.append(alt_product)
            
            # Sort by similarity score
            alternatives.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            logger.info(f"Found {len(alternatives)} alternatives for {product_id}")
            return alternatives[:5]  # Return top 5
            
        except Exception as e:
            logger.error(f"Error finding alternatives for {product_id}: {e}")
            return []
    
    async def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Search products by category."""
        try:
            all_products = get_all_products()
            category_products = []
            
            for product_id, product in all_products.items():
                if product.get("category", "").lower() == category.lower():
                    product_info = product.copy()
                    product_info["product_id"] = product_id
                    category_products.append(product_info)
            
            # Sort by rating and price
            category_products.sort(key=lambda x: (-x["rating"], x["price"]))
            
            logger.info(f"Found {len(category_products)} products in category {category}")
            return category_products
            
        except Exception as e:
            logger.error(f"Error searching category {category}: {e}")
            return []
    
    async def get_recommendations(self, customer_needs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get product recommendations based on customer needs."""
        try:
            all_products = get_all_products()
            recommendations = []
            
            for product_id, product in all_products.items():
                match_score = self._calculate_need_match(product, customer_needs)
                if match_score > 0.5:  # Threshold for recommendation
                    rec_product = product.copy()
                    rec_product["product_id"] = product_id
                    rec_product["match_score"] = match_score
                    rec_product["why_recommended"] = self._explain_recommendation(product, customer_needs)
                    recommendations.append(rec_product)
            
            # Sort by match score
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations[:3]  # Return top 3
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _get_availability_status(self, inventory: int) -> str:
        """Determine availability status based on inventory level."""
        if inventory >= 50:
            return "In Stock"
        elif inventory >= 10:
            return "Limited Stock"
        elif inventory > 0:
            return "Low Stock"
        else:
            return "Out of Stock"
    
    def _classify_price_tier(self, price: float) -> str:
        """Classify product into price tier."""
        if price < 700:
            return "Budget"
        elif price < 1200:
            return "Mid-Range"
        elif price < 1800:
            return "Premium"
        else:
            return "High-End"
    
    def _estimate_restock(self, inventory: int) -> str:
        """Estimate restock timeline based on current inventory."""
        if inventory >= 10:
            return "No restock needed"
        elif inventory > 0:
            return "1-2 weeks"
        else:
            return "2-4 weeks"
    
    def _create_comparison_matrix(self, products: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a comparison matrix for products."""
        if not products:
            return {}
        
        # Extract common comparison points
        specs_comparison = {}
        price_comparison = {}
        ratings_comparison = {}
        
        for product_id, product in products.items():
            specs_comparison[product_id] = product.get("specs", {})
            price_comparison[product_id] = product.get("price", 0)
            ratings_comparison[product_id] = product.get("rating", 0)
        
        return {
            "specifications": specs_comparison,
            "prices": price_comparison,
            "ratings": ratings_comparison,
            "best_value": min(price_comparison, key=price_comparison.get),
            "highest_rated": max(ratings_comparison, key=ratings_comparison.get)
        }
    
    def _generate_recommendations(self, products: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Generate recommendations based on product comparison."""
        if not products:
            return {}
        
        recommendations = {}
        
        # Find best value
        best_value = min(products.items(), key=lambda x: x[1]["price"])
        recommendations["best_value"] = f"{best_value[1]['name']} offers the best price at ${best_value[1]['price']}"
        
        # Find highest rated
        highest_rated = max(products.items(), key=lambda x: x[1]["rating"])
        recommendations["highest_rated"] = f"{highest_rated[1]['name']} has the highest rating at {highest_rated[1]['rating']}"
        
        return recommendations
    
    def _calculate_similarity(self, product1: Dict[str, Any], product2: Dict[str, Any], criteria: str) -> float:
        """Calculate similarity score between two products."""
        score = 0.0
        
        # Category match
        if product1.get("category") == product2.get("category"):
            score += 0.4
        
        # Price range similarity
        price_diff = abs(product1["price"] - product2["price"]) / max(product1["price"], product2["price"])
        score += (1 - price_diff) * 0.3
        
        # Specs similarity (simplified)
        specs1 = product1.get("specs", {})
        specs2 = product2.get("specs", {})
        common_specs = set(specs1.keys()) & set(specs2.keys())
        if common_specs:
            spec_matches = sum(1 for spec in common_specs if specs1[spec] == specs2[spec])
            score += (spec_matches / len(common_specs)) * 0.3
        
        return min(score, 1.0)
    
    def _identify_differences(self, product1: Dict[str, Any], product2: Dict[str, Any]) -> List[str]:
        """Identify key differences between products."""
        differences = []
        
        # Price difference
        price_diff = product2["price"] - product1["price"]
        if abs(price_diff) > 50:
            if price_diff > 0:
                differences.append(f"${abs(price_diff):.0f} more expensive")
            else:
                differences.append(f"${abs(price_diff):.0f} less expensive")
        
        # Category difference
        if product1.get("category") != product2.get("category"):
            differences.append(f"Different category: {product2.get('category', 'Unknown')}")
        
        return differences
    
    def _calculate_need_match(self, product: Dict[str, Any], needs: Dict[str, Any]) -> float:
        """Calculate how well a product matches customer needs."""
        score = 0.0
        total_criteria = 0
        
        # Budget match
        if "max_budget" in needs:
            total_criteria += 1
            if product["price"] <= needs["max_budget"]:
                score += 1.0
            elif product["price"] <= needs["max_budget"] * 1.2:  # Within 20%
                score += 0.5
        
        # Category preference
        if "preferred_category" in needs:
            total_criteria += 1
            if product.get("category") == needs["preferred_category"]:
                score += 1.0
        
        # Use case match (simplified)
        if "use_case" in needs:
            total_criteria += 1
            use_case = needs["use_case"].lower()
            category = product.get("category", "").lower()
            
            match_map = {
                "gaming": "gaming",
                "business": "professional",
                "student": "budget",
                "travel": "ultrabook"
            }
            
            if match_map.get(use_case) == category:
                score += 1.0
            elif category in ["professional", "ultrabook"]:  # Versatile options
                score += 0.6
        
        return score / max(total_criteria, 1)
    
    def _explain_recommendation(self, product: Dict[str, Any], needs: Dict[str, Any]) -> str:
        """Explain why a product is recommended."""
        reasons = []
        
        if "max_budget" in needs and product["price"] <= needs["max_budget"]:
            reasons.append("fits your budget")
        
        if "preferred_category" in needs and product.get("category") == needs["preferred_category"]:
            reasons.append(f"matches your preference for {needs['preferred_category']} laptops")
        
        if product["rating"] >= 4.5:
            reasons.append("highly rated by customers")
        
        if not reasons:
            reasons.append("good overall value")
        
        return "Recommended because it " + " and ".join(reasons)

# Global product tools instance
product_tools = ProductTools()
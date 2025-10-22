# 🎭 Demo Questions for Multi-Agent Customer Care System

This guide provides curated questions and scenarios to showcase the multi-agent system's capabilities during demonstrations.

## 🎯 **Primary Demo Scenario (Start Here)**

### **Question 1:** 
```
"My laptop order #12345 won't turn on, I need help!"
```

**What This Demonstrates:**
- **Multi-agent coordination** (Order + Tech Support + Solutions agents)
- **Context sharing** between agents (order info flows to tech support)
- **Conditional execution** (agents execute based on dependencies)
- **Tool integration** (order lookup, knowledge base, troubleshooting)
- **Response synthesis** (unified customer service response)

**Expected Agent Flow:**
1. 🤖 **Order Agent** → Retrieves order details, warranty info
2. 🔧 **Tech Support Agent** → Provides troubleshooting steps
3. 💡 **Solutions Agent** → Offers resolution options
4. 🎯 **Orchestrator** → Synthesizes all responses

---

## 🔄 **Follow-up Questions (Memory & Context)**

### **Question 2 (after Question 1):**
```
"What other laptops do you have in similar price range?"
```

**What This Demonstrates:**
- **Memory persistence** (remembers previous order #12345)
- **Context awareness** (knows customer had TechBook Pro 15)
- **Product agent activation** with comparison tools
- **Cross-agent context sharing**

### **Question 3 (after Question 2):**
```
"What would you recommend for gaming instead?"
```

**What This Demonstrates:**
- **Conversation continuity**
- **Preference learning** (now knows customer wants gaming)
- **Product recommendations** based on use case
- **Alternative product suggestions**

---

## 🛒 **Order Support Scenarios**

### **Order Tracking:**
```
"Can you help me track order #12346?"
```
- Single-agent response (Order Agent only)
- Order lookup and tracking tools
- Delivery status information

### **Warranty Questions:**
```
"Is my order #12345 still under warranty?"
```
- Order Agent + warranty policy lookup
- Date calculations and coverage details

### **Return Request:**
```
"I want to return my order #12345 because it's defective"
```
- Order Agent + Solutions Agent coordination
- Return policy lookup and processing
- Reason-based return handling

---

## 💻 **Product Comparison Scenarios**

### **Direct Comparison:**
```
"Compare TechBook Pro 15 vs TechBook Air 13"
```
- Product Agent with comparison tools
- Specification analysis
- Recommendation engine

### **Budget-Based Search:**
```
"Show me all laptops under $1000"
```
- Product catalog search
- Inventory checking
- Budget filtering

### **Use Case Recommendations:**
```
"I need a laptop for video editing and graphic design"
```
- Needs analysis
- Performance-based recommendations
- Feature matching

---

## 🔧 **Technical Support Scenarios**

### **Performance Issues:**
```
"My laptop is running very slowly and freezing"
```
- Tech Support Agent activation
- Knowledge base search
- Troubleshooting workflow
- Escalation options

### **Hardware Problems:**
```
"My laptop screen is flickering and has dark spots"
```
- Hardware diagnosis
- Warranty consideration
- Repair vs replacement options

### **Connectivity Issues:**
```
"I can't connect to WiFi on my new laptop"
```
- Network troubleshooting
- Step-by-step guidance
- Driver and configuration checks

---

## 💡 **Complex Problem Resolution**

### **Multi-Issue Scenario:**
```
"My order #12346 arrived late, the laptop overheats, and I'm not happy with the performance"
```

**What This Demonstrates:**
- **Multiple agent coordination** (Order + Tech Support + Solutions)
- **Parallel issue handling**
- **Escalation management**
- **Customer satisfaction focus**

### **Escalation Scenario:**
```
"I've tried everything you suggested but my laptop still doesn't work. This is unacceptable!"
```

**What This Demonstrates:**
- **Sentiment analysis** (frustration detection)
- **Solutions Agent priority** (compensation/escalation)
- **Customer retention strategies**
- **Manager escalation protocols**

---

## 🎪 **Demo Flow Suggestions**

### **5-Minute Demo Flow:**
1. **Start with primary scenario** (Question 1) - Shows full coordination
2. **Ask follow-up** (Question 2) - Shows memory
3. **Try different category** (Order tracking) - Shows versatility
4. **Show reset** - Demonstrate memory clearing

### **10-Minute Demo Flow:**
1. **Primary scenario** + follow-ups (Questions 1-3)
2. **New order scenario** (Different order number)
3. **Technical support** scenario
4. **Complex multi-issue** scenario
5. **Reset and quick comparison** demo

### **15-Minute Deep Dive:**
- Follow 10-minute flow
- Add budget-based search
- Show escalation handling
- Demonstrate all execution modes (sequential, parallel, conditional)
- Explain memory persistence across conversation

---

## 🎨 **Visual Elements to Highlight**

### **In the Streamlit Interface:**
- **Agent badges** changing color as they activate
- **Memory panel** updating with order numbers and products
- **Execution plan** showing step-by-step coordination
- **Agent activity** real-time status updates
- **Conversation persistence** across multiple questions

### **Key Talking Points:**
- "Notice how the Order Agent information flows to Tech Support"
- "See how the system remembers the laptop model from the order"
- "Watch multiple agents working in parallel vs sequential"
- "The memory panel shows context being built across conversation"
- "Each agent has specialized tools and knowledge"

---

## 🚀 **Advanced Demo Scenarios**

### **Cross-Session Memory Test:**
1. Ask about order #12345
2. Reset conversation  
3. Ask "What was my previous order?" (should not remember)
4. Ask about order #12345 again (fresh context)

### **Agent Coordination Comparison:**
1. Simple question → Single agent (fast)
2. Complex question → Multiple agents (comprehensive)
3. Show execution time differences

### **Tool Integration Showcase:**
1. Order lookup tools
2. Knowledge base search
3. Product comparison tools
4. Web search capabilities (if API keys configured)

---

## 📝 **Presenter Notes**

### **What to Emphasize:**
- ✅ **Real AI agents** (not just scripted responses)
- ✅ **Intelligent coordination** (not just keyword matching)
- ✅ **Memory and context** (true conversation state)
- ✅ **Tool integration** (accessing multiple data sources)
- ✅ **Graceful handling** (errors, timeouts, fallbacks)

### **Technical Details to Mention:**
- OpenAI GPT-4 for agent reasoning
- Google Gemini for web search capabilities
- FastAPI backend with async processing
- Real-time agent coordination and planning
- 30-second timeout protection

---

## 🎭 **Troubleshooting Demo Issues**

### **If Response is Slow:**
- Mention "Real AI processing in progress"
- Show agent activity indicators
- Explain 30-second timeout protection

### **If API Keys Missing:**
- System gracefully falls back to mock responses
- Still demonstrates coordination and planning
- Highlight architecture and design

### **If Error Occurs:**
- Show error handling and recovery
- Demonstrate system resilience
- Reset conversation and continue

---

This guide ensures your demo showcases the full capabilities of the multi-agent system while keeping the audience engaged with realistic customer service scenarios.
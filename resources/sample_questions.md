# Bhumi Vikas Sahayak - 17 Benchmark Test Questions

This benchmark dataset contains 17 representative questions tested against the MP Bhumi Vikas Rules, 2012 (consolidated to 6 March 2025). 15 questions test verified rule citation and calculation capabilities; 2 test rejection of questions outside the scope of Bhumi Vikas Rules.

---

### Question 1 (Front Setback - Residential)
- **ID**: Q01
- **Language**: English
- **Question**: My plot is 200 sq m on a 9 m road. How much front open space (FMOS) do I need to leave for a residential building?
- **Expected Rule**: Rule 56(1)(a)
- **Expected Values**: {"front_mos": 3.0}
- **Answerable**: true

### Question 2 (Front Setback - Hindi)
- **ID**: Q02
- **Language**: Hindi
- **Question**: 15 मीटर चौड़ी सड़क पर 300 वर्ग मीटर के आवासीय प्लॉट के लिए सामने कितना खुला स्थान (Front MOS) छोड़ना होगा?
- **Expected Rule**: Rule 56(1)(a)
- **Expected Values**: {"front_mos": 4.5}
- **Answerable**: true

### Question 3 (Rear Setback - Residential)
- **ID**: Q03
- **Language**: English
- **Question**: For a residential building up to 12.5 meters height on a plot area of 180 sq m, what is the required rear open space?
- **Expected Rule**: Rule 56(2)(a)
- **Expected Values**: {"rear_mos": 2.5}
- **Answerable**: true

### Question 4 (Rear Setback - Small Plot)
- **ID**: Q04
- **Language**: English
- **Question**: What is the minimum rear open space required for a residential plot of 35 sq meters?
- **Expected Rule**: Rule 56(2)(a)
- **Expected Values**: {"rear_mos": 0.0}
- **Answerable**: true

### Question 5 (Side Setback - Detached Building)
- **ID**: Q05
- **Language**: Hindi
- **Question**: 250 वर्ग मीटर के डिटैच्ड (एकल) आवासीय मकान के लिए दोनों तरफ कितना साइड ओपन स्पेस छोड़ना जरूरी है?
- **Expected Rule**: Rule 56(3)(i)
- **Expected Values**: {"side_mos": 3.0}
- **Answerable**: true

### Question 6 (Farm House Norms)
- **ID**: Q06
- **Language**: English
- **Question**: What is the minimum plot size and maximum FAR allowed for a Farm House in an agricultural zone?
- **Expected Rule**: Rule 17
- **Expected Values**: {"min_plot_hectare": 0.40, "max_far": 0.10, "max_height": 7.5}
- **Answerable**: true

### Question 7 (Electric Line Clearance - High Voltage)
- **ID**: Q07
- **Language**: English
- **Question**: What is the minimum vertical and horizontal clearance required from a 33000-volt high-voltage electric line to a building?
- **Expected Rule**: Rule 52
- **Expected Values**: {"vertical_clearance": 3.7, "horizontal_clearance": 1.2}
- **Answerable**: true

### Question 8 (Electric Line Clearance - Low/Medium Voltage Hindi)
- **ID**: Q08
- **Language**: Hindi
- **Question**: लो और मीडियम वोल्टेज बिजली की लाइन से किसी इमारत की न्यूनतम ऊर्ध्वाधर (vertical) और क्षैतिज (horizontal) दूरी कितनी होनी चाहिए?
- **Expected Rule**: Rule 52
- **Expected Values**: {"vertical_clearance": 2.5, "horizontal_clearance": 1.2}
- **Answerable**: true

### Question 9 (Building Permission Fees - Residential)
- **ID**: Q09
- **Language**: English
- **Question**: What is the permission fee for a residential building with a proposed built-up area of 180 sq meters?
- **Expected Rule**: Rule 21(3)(b)
- **Expected Values**: {"permission_fee": 2000.0}
- **Answerable**: true

### Question 10 (Commercial Building Permission Fee Hindi)
- **ID**: Q10
- **Language**: Hindi
- **Question**: 250 वर्ग मीटर बिल्ट-अप एरिया की दुकान/वाणिज्यिक भवन के लिए अनुमति शुल्क (permission fee) कितना देय होगा?
- **Expected Rule**: Rule 21(3)(b)
- **Expected Values**: {"permission_fee": 4500.0}
- **Answerable**: true

### Question 11 (High Rise Definition)
- **ID**: Q11
- **Language**: English
- **Question**: According to MP Bhumi Vikas Rules, what qualifies as a high rise building in terms of storeys or height?
- **Expected Rule**: Rule 2(38)
- **Expected Values**: {"more_than_stories": 10, "more_than_height": 30.0}
- **Answerable**: true

### Question 12 (Permissible Deviation in Sanctioned Plan)
- **ID**: Q12
- **Language**: English
- **Question**: Under Rule 24, up to what percentage can deviation from a sanctioned plan be permitted in FAR without violating the rule?
- **Expected Rule**: Rule 24(1)(b)
- **Expected Values**: {"max_far_deviation_pct": 30.0}
- **Answerable**: true

### Question 13 (Deemed Instant Approval - Rule 12-A)
- **ID**: Q13
- **Language**: Hindi
- **Question**: कितने वर्ग मीटर तक के आवासीय भूखंडों पर तत्काल या डीम्ड भवन अनुज्ञा (instant/deemed approval) का प्रावधान नियम 12-A में है?
- **Expected Rule**: Rule 12-A
- **Expected Values**: {"max_plot_sqm": 186.0}
- **Answerable**: true

### Question 14 (Sanction Validity Duration)
- **ID**: Q14
- **Language**: English
- **Question**: How long does a development permission granted under Section 30 remain valid, and for how long can it be revalidated?
- **Expected Rule**: Rule 23
- **Expected Values**: {"validity_years": 3, "revalidation_terms": 2, "revalidation_years_each": 1}
- **Answerable**: true

### Question 15 (Standard Residential FAR)
- **ID**: Q15
- **Language**: English
- **Question**: What is the standard Base Floor Area Ratio (FAR) prescribed for general residential use group in Table 8?
- **Expected Rule**: Rule 61
- **Expected Values**: {"residential_far": 1.25}
- **Answerable**: true

### Question 16 (Unanswerable 1 - Municipal Property Tax)
- **ID**: Q16
- **Language**: English
- **Question**: What is the quarterly property tax rate per square foot for residential properties in Zone 4 of Bhopal Municipal Corporation?
- **Expected Rule**: null
- **Expected Values**: null
- **Answerable**: false
- **Note**: The Bhumi Vikas Rules govern land development and building construction permissions, not municipal property tax assessments. The system must answer that the rules do not cover this.

### Question 17 (Unanswerable 2 - Municipal Water Meter Tariff Hindi)
- **ID**: Q17
- **Language**: Hindi
- **Question**: भोपाल नगर निगम में नए घरेलू नल कनेक्शन के लिए प्रतिमाह जल उपकर (water tariff) और सिक्योरिटी डिपॉजिट कितना लगेगा?
- **Expected Rule**: null
- **Expected Values**: null
- **Answerable**: false
- **Note**: Water supply tariff rates are governed by municipal corporation byelaws, not MP Bhumi Vikas Rules. The system must report not found / rules do not cover this.

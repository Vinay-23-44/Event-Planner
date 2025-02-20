# ===========================
# BACKEND (Data Processing)
# ===========================

# Import necessary libraries
import streamlit as st
import pandas as pd
import re

# Function to load and process venue data
@st.cache_data
def load_data():
    """Loads and processes venue data from CSV."""
    venues = pd.read_csv("venues.csv")

    # Ensure correct column names (remove unwanted spaces)
    venues.columns = venues.columns.str.strip()

    # Convert 'Capacity' column to integer (handling ranges like "100-500")
    def parse_capacity(cap):
        if isinstance(cap, str) and re.match(r"^\d+(-\d+)?$", cap):
            return int(cap.split("-")[-1])  # Get highest value in range
        try:
            return int(cap)
        except ValueError:
            return None  # Handle invalid values

    venues["Capacity"] = venues["Capacity"].apply(parse_capacity)
    venues = venues.dropna(subset=["Capacity"])  # Remove empty values
    venues["Capacity"] = venues["Capacity"].astype(int)

    # Convert 'Budget' column to integer (removing ₹ symbol & commas)
    venues["Budget"] = venues["Budget"].replace({"₹": "", ",": ""}, regex=True).astype(int)

    return venues

# Load venue data (Cached for performance)
venues = load_data()

# ===========================
# FRONTEND (User Interface)
# ===========================

# Title and description
st.title("🎪 AI-Powered Event Planner")
st.write("Plan your event step-by-step with smart venue and budget recommendations!")

# ---------------------------------------
# User Inputs (Event Planning Filters)
# ---------------------------------------

# Step 1: Select Event Type
event_type = st.selectbox("🎭 Select Event Type:", 
    ["Wedding", "Corporate Event", "Birthday", "Conference", "Concert", "Exhibition"])

# Step 2: Select Location
locations = venues["Location"].unique()
selected_location = st.selectbox("📍 Select Location:", ["Any"] + list(locations))

# Step 3: Select Number of Attendees
attendees = st.slider("👥 Number of attendees:", min_value=10, max_value=5000, step=10, value=100)

# Step 4: Select Budget
budget = st.slider("💰 Select Your Budget (₹):", min_value=5000, max_value=200000, step=5000, value=50000)

# Step 5: Select Venue Type
venue_type = st.radio("🏢 Select Venue Type:", ["Indoor", "Outdoor", "Any"])

# Step 6: Select Required Amenities
amenities_list = ["Mic", "Projector", "Sound System", "Lighting", "WiFi", "Seating", "Catering", "Valet Parking"]
selected_amenities = st.multiselect("🎤 Select Required Amenities:", amenities_list)

# ===========================
# BACKEND (Filtering Data)
# ===========================

# Apply venue filters based on user selections
filtered_venues = venues[
    (venues["Capacity"] >= attendees) & 
    (venues["Budget"] <= budget) & 
    (venues["Event Type"].str.contains(event_type, case=False, na=False))
]

if venue_type != "Any":
    filtered_venues = filtered_venues[filtered_venues["Type"].str.lower() == venue_type.lower()]

if selected_location != "Any":
    filtered_venues = filtered_venues[filtered_venues["Location"] == selected_location]

if selected_amenities:
    filtered_venues = filtered_venues[
        filtered_venues["Available Equipments"].apply(lambda x: all(item in x for item in selected_amenities))
    ]

# ===========================
# FRONTEND (Display Results)
# ===========================

# Step 7: Show Recommended Venues
st.subheader("🏠 Recommended Venues:")
if not filtered_venues.empty:
    st.success(f"✅ Found {len(filtered_venues)} matching venues!")
    st.dataframe(filtered_venues[["Venue Name", "Location", "Capacity", "Type", "Budget", "Event Type"]])

    # 📥 Download Venue List
    csv = filtered_venues.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Venue List", csv, "recommended_venues.csv", "text/csv")
else:
    st.warning("⚠️ No venues match your criteria. Try adjusting your filters.")

# Step 8: Show Event Plan Summary
st.subheader("📋 Your Event Plan:")
event_summary = {
    "Event Type": event_type,
    "Location": selected_location,
    "Number of Attendees": attendees,
    "Budget": f"₹{budget}",
    "Venue Type": venue_type,
    "Selected Amenities": ", ".join(selected_amenities) if selected_amenities else "None",
}
st.json(event_summary)

# Download Full Event Plan
event_summary_df = pd.DataFrame([event_summary])
csv_plan = event_summary_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Event Plan", csv_plan, "event_plan.csv", "text/csv")

# Footer
st.write("---")
st.write("Developed by Vinay Dahiya")

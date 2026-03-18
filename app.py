"""Shah Family NYC Guide — Flask backend with AI chatbot."""
import os
import json
import time
import hashlib
from collections import defaultdict
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
RATE_LIMIT = 30  # requests per hour per IP
rate_store = defaultdict(list)

# All 47 spots with coordinates
SPOTS = [
    {"name":"Tompkins Square Bagels","lat":40.7264,"lng":-73.9787,"category":"food","subcategory":"bagels","starred":True,"address":"165 Avenue A, East Village","distanceText":"25 min subway","description":"The best bagels in the city. Hand-rolled, kettle-boiled, perfect chew. Get there early.","tip":"F from 23rd St to 2nd Ave"},
    {"name":"Ess-A-Bagel","lat":40.7579,"lng":-73.9680,"category":"food","subcategory":"bagels","starred":True,"address":"831 3rd Ave, Midtown East","distanceText":"20 min subway","description":"Classic NYC bagel institution. Massive bagels, generous spreads.","tip":""},
    {"name":"Modern Bread and Bagel","lat":40.7453,"lng":-73.9893,"category":"food","subcategory":"bagels","starred":True,"address":"25 W 28th St","distanceText":"5 min walk","description":"Gluten-free and allergy-friendly bakery. 28th St location is walking distance!","tip":"5 min walk from apartment"},
    {"name":"Russ & Daughters","lat":40.7223,"lng":-73.9879,"category":"food","subcategory":"bagels","starred":False,"address":"179 E Houston St, LES","distanceText":"20 min subway","description":"Iconic appetizing shop since 1914. Lox, bagels, whitefish.","tip":""},
    {"name":"Clinton St. Baking Company","lat":40.7207,"lng":-73.9837,"category":"food","subcategory":"bagels","starred":False,"address":"4 Clinton St, LES","distanceText":"20 min subway","description":"Famous for pancakes and brunch. Blueberry pancakes are legendary.","tip":""},
    {"name":"Joe's Pizza","lat":40.7306,"lng":-73.9989,"category":"food","subcategory":"pizza","starred":True,"address":"7 Carmine St, Greenwich Village","distanceText":"15 min walk","description":"THE classic NYC slice. No frills, perfect New York cheese slice.","tip":""},
    {"name":"Chelsea Market","lat":40.7424,"lng":-74.0061,"category":"food","subcategory":"casual","starred":False,"address":"75 9th Ave, Chelsea","distanceText":"10 min walk","description":"Food hall in converted Nabisco factory. Los Tacos No. 1, Lobster Place, Dizengoff.","tip":""},
    {"name":"Prince Street Pizza","lat":40.7230,"lng":-73.9945,"category":"food","subcategory":"pizza","starred":False,"address":"27 Prince St, Nolita","distanceText":"20 min subway","description":"Famous pepperoni square (Soho Square) — thick Sicilian with crispy cup pepperoni.","tip":""},
    {"name":"Xi'an Famous Foods","lat":40.7367,"lng":-73.9968,"category":"food","subcategory":"casual","starred":False,"address":"34 W 14th St","distanceText":"10 min walk","description":"Hand-pulled noodles, spicy cumin lamb. Real NYC cheap-eats.","tip":""},
    {"name":"Katz's Delicatessen","lat":40.7223,"lng":-73.9874,"category":"food","subcategory":"casual","starred":False,"address":"205 E Houston St, LES","distanceText":"20 min subway","description":"Most famous deli in America since 1888. Pastrami on rye is life-changing.","tip":""},
    {"name":"L'Industrie Pizzeria","lat":40.7113,"lng":-73.9577,"category":"food","subcategory":"pizza","starred":True,"address":"254 S 2nd St, Williamsburg","distanceText":"30 min subway","description":"Arguably best pizza in NYC. Thin, crispy, fresh burrata on top.","tip":"L train to Bedford Ave"},
    {"name":"Rubirosa","lat":40.7225,"lng":-73.9958,"category":"food","subcategory":"pizza","starred":True,"address":"235 Mulberry St, Nolita","distanceText":"20 min subway","description":"Thin-crust Italian-American. Vodka pizza is legendary. We've been here multiple times.","tip":"Make reservation on Resy"},
    {"name":"Carbone","lat":40.7303,"lng":-74.0005,"category":"food","subcategory":"finedining","starred":False,"address":"181 Thompson St, Greenwich Village","distanceText":"15 min walk","description":"Italian-American fine dining with retro vibes. Spicy rigatoni vodka is famous.","tip":"Hard to get a reservation"},
    {"name":"Via Carota","lat":40.7320,"lng":-74.0032,"category":"food","subcategory":"finedining","starred":False,"address":"51 Grove St, West Village","distanceText":"15 min walk","description":"Rustic Italian — seasonal, simple, perfect. Carciofi fried artichokes are legendary.","tip":"Walk-ins only, go early 5:30 PM"},
    {"name":"The Smith","lat":40.7365,"lng":-73.9905,"category":"food","subcategory":"casual","starred":False,"address":"1900 Broadway, Union Square","distanceText":"10 min walk","description":"Solid American bistro. Good cocktails, reliable food.","tip":""},
    {"name":"Masala Times","lat":40.7298,"lng":-73.9998,"category":"food","subcategory":"indian","starred":True,"address":"194 Bleecker St, Greenwich Village","distanceText":"15 min walk","description":"Good Indian food in the Village. Solid for something familiar.","tip":""},
    {"name":"Adda Indian Canteen","lat":40.7448,"lng":-73.9233,"category":"food","subcategory":"indian","starred":False,"address":"31-31 Thomson Ave, LIC Queens","distanceText":"25 min subway","description":"One of the best Indian restaurants — Michelin-recognized. Worth the trip to Queens.","tip":"7 train from 34th St"},
    {"name":"Dhamaka","lat":40.7264,"lng":-73.9847,"category":"food","subcategory":"indian","starred":False,"address":"119 1st Ave, East Village","distanceText":"25 min subway","description":"Regional Indian food you can't find elsewhere. Michelin Bib Gourmand.","tip":""},
    {"name":"Indian Accent","lat":40.7643,"lng":-73.9779,"category":"food","subcategory":"indian","starred":True,"address":"123 W 56th St, Midtown","distanceText":"25 min subway","description":"One of the most celebrated Indian restaurants in the world. Manish Mehrotra's NYC outpost.","tip":"F to 57th St"},
    {"name":"Tamarind Tribeca","lat":40.7195,"lng":-74.0089,"category":"food","subcategory":"indian","starred":False,"address":"99 Hudson St, Tribeca","distanceText":"20 min subway","description":"Upscale Indian — beautiful space, refined food. Lamb chops and tandoori excellent.","tip":""},
    {"name":"HanGawi","lat":40.7476,"lng":-73.9833,"category":"food","subcategory":"indian","starred":True,"address":"12 E 32nd St, Koreatown","distanceText":"10 min walk","description":"Fully vegan Korean — Jain-friendly (no onion, no garlic). Shoes off, low tables. Beautiful and meditative.","tip":""},
    {"name":"Bungalow","lat":40.7232,"lng":-73.9876,"category":"food","subcategory":"indian","starred":False,"address":"24 First Ave, East Village","distanceText":"25 min subway","description":"Chef Vikas Khanna's Michelin-starred flagship. Condé Nast's best new restaurants in the world.","tip":"Sun-Wed 5-10:30 PM, Thu-Sat 5-11 PM. Reserve ahead!"},
    {"name":"GupShup","lat":40.7430,"lng":-73.9815,"category":"food","subcategory":"indian","starred":True,"address":"105 Lexington Ave, Gramercy/Curry Hill","distanceText":"10 min walk","description":"Bungalow's sister restaurant — same team, more casual. Modern Indian street food and cocktails.","tip":"Right in Curry Hill, easy walk from the apartment"},
    {"name":"Baar Baar","lat":40.7253,"lng":-73.9901,"category":"food","subcategory":"indian","starred":True,"address":"22 E 1st St, East Village","distanceText":"20 min subway","description":"Modern Indian — stylish space, creative cocktails, elevated classics. Great small plates for sharing.","tip":""},
    {"name":"The Kati Roll Company","lat":40.7302,"lng":-74.0003,"category":"food","subcategory":"indian","starred":True,"address":"99 MacDougal St, Village (also 39 W 46th St)","distanceText":"15 min walk","description":"Kolkata-style kati rolls — Indian burritos. Cheap, fast, delicious. Midtown location near Broadway.","tip":"Two locations: MacDougal St or 46th St near Times Square"},
    {"name":"Curry Hill","lat":40.7440,"lng":-73.9830,"category":"food","subcategory":"indian","starred":False,"address":"Lexington Ave, 26th-30th St","distanceText":"5-10 min walk","description":"A strip of Indian restaurants — Patiala, Dhaba, Chennai Garden, Tiffin Wallah. Not fancy but convenient and authentic.","tip":"5-10 minute walk east from the apartment"},
    {"name":"Levain Bakery","lat":40.7804,"lng":-73.9768,"category":"food","subcategory":"dessert","starred":False,"address":"167 W 74th St, Upper West Side","distanceText":"20 min subway","description":"Massive, gooey, underbaked cookies — chocolate chip walnut is iconic.","tip":""},
    {"name":"Magnolia Bakery","lat":40.7355,"lng":-74.0029,"category":"food","subcategory":"dessert","starred":False,"address":"401 Bleecker St, West Village","distanceText":"15 min walk","description":"Classic cupcakes and banana pudding. The banana pudding is the move here.","tip":""},
    {"name":"Dominique Ansel Bakery","lat":40.7235,"lng":-73.9994,"category":"food","subcategory":"dessert","starred":False,"address":"189 Spring St, Soho","distanceText":"20 min subway","description":"Inventor of the Cronut. The DKA (Kouign Amann) is incredible.","tip":""},
    {"name":"Joe Coffee","lat":40.7427,"lng":-73.9939,"category":"food","subcategory":"dessert","starred":False,"address":"131 W 21st St","distanceText":"3 min walk","description":"One of the best local coffee chains in NYC. Practically at your doorstep.","tip":""},
    {"name":"9/11 Memorial & Museum","lat":40.7115,"lng":-74.0134,"category":"sightseeing","subcategory":"mustdo","starred":True,"address":"180 Greenwich St, Financial District","distanceText":"20 min subway","description":"Two massive waterfalls in the footprints of the Twin Towers. Museum below is intense but powerful. Give it 2-3 hours.","tip":"1 train from 23rd St to Chambers St. Book museum tickets online."},
    {"name":"The High Line","lat":40.7480,"lng":-74.0048,"category":"sightseeing","subcategory":"mustdo","starred":False,"address":"Gansevoort St to 34th St","distanceText":"5-15 min walk","description":"Elevated park on old freight rail tracks. Art installations, Hudson views, gardens.","tip":"Multiple entrances along the west side"},
    {"name":"Central Park","lat":40.7829,"lng":-73.9654,"category":"sightseeing","subcategory":"mustdo","starred":False,"address":"59th to 110th St","distanceText":"15 min subway","description":"Walk the southern end: Bethesda Fountain, Bow Bridge, Strawberry Fields.","tip":"Subway to Columbus Circle entrance"},
    {"name":"Top of the Rock","lat":40.7593,"lng":-73.9794,"category":"sightseeing","subcategory":"mustdo","starred":False,"address":"30 Rockefeller Plaza, Midtown","distanceText":"15 min subway","description":"Better views than Empire State because you can SEE the Empire State. Go at sunset.","tip":"Book online"},
    {"name":"Brooklyn Bridge Walk","lat":40.7061,"lng":-73.9969,"category":"sightseeing","subcategory":"mustdo","starred":False,"address":"City Hall area (Manhattan side)","distanceText":"25 min subway","description":"Walk across into DUMBO. Manhattan skyline views from Brooklyn are postcard-perfect.","tip":""},
    {"name":"The Vessel / Hudson Yards","lat":40.7536,"lng":-74.0022,"category":"sightseeing","subcategory":"unique","starred":False,"address":"20 Hudson Yards","distanceText":"10 min walk","description":"Honeycomb-shaped structure — architecturally wild. The Shops at Hudson Yards are fancy.","tip":""},
    {"name":"Grand Central Terminal","lat":40.7527,"lng":-73.9772,"category":"sightseeing","subcategory":"unique","starred":False,"address":"89 E 42nd St, Midtown","distanceText":"15 min subway","description":"Beaux-Arts masterpiece. Look up at the constellation ceiling. Try the Whispering Gallery.","tip":"4/5/6 from 23rd St to Grand Central"},
    {"name":"Little Island","lat":40.7425,"lng":-74.0098,"category":"sightseeing","subcategory":"unique","starred":False,"address":"Pier 55, W 13th St, Hudson River","distanceText":"15 min walk","description":"Park built on tulip-shaped pillars in the Hudson River. Free, beautiful gardens.","tip":""},
    {"name":"Washington Square Park","lat":40.7308,"lng":-73.9973,"category":"sightseeing","subcategory":"unique","starred":False,"address":"Greenwich Village","distanceText":"15 min walk","description":"The arch, the fountain, the chess players, the performers — heartbeat of the Village.","tip":""},
    {"name":"Harry Potter Store","lat":40.7409,"lng":-73.9897,"category":"sightseeing","subcategory":"unique","starred":True,"address":"935 Broadway (corner of 22nd St)","distanceText":"2 min walk","description":"Three floors of immersive magical retail. Butterbeer, wand fitting. We visited July 2025.","tip":"Literally 2 min walk from the apartment!"},
    {"name":"Flatiron Building","lat":40.7411,"lng":-73.9897,"category":"sightseeing","subcategory":"unique","starred":False,"address":"175 5th Ave (23rd & Broadway)","distanceText":"5 min walk","description":"The iconic triangular building, recently restored.","tip":""},
    {"name":"Chelsea Galleries","lat":40.7480,"lng":-74.0042,"category":"sightseeing","subcategory":"unique","starred":False,"address":"19th-28th St, west of 10th Ave","distanceText":"10 min walk","description":"Largest concentration of art galleries in the world. Free to browse.","tip":""},
    {"name":"The Lion King","lat":40.7580,"lng":-73.9855,"category":"broadway","subcategory":"musical","starred":True,"address":"Minskoff Theatre, 200 W 45th St","distanceText":"20 min subway","description":"The gold standard of Broadway spectacle. Puppetry, music, the opening Circle of Life — breathtaking.","tip":"Book on TodayTix or TKTS for discounted tickets"},
    {"name":"Aladdin","lat":40.7566,"lng":-73.9878,"category":"broadway","subcategory":"musical","starred":True,"address":"New Amsterdam Theatre, 214 W 42nd St","distanceText":"20 min subway","description":"Pure fun. Genie steals the show. Colorful, energetic, crowd-pleasing.","tip":""},
    {"name":"Wicked","lat":40.7622,"lng":-73.9844,"category":"broadway","subcategory":"musical","starred":False,"address":"Gershwin Theatre, 222 W 51st St","distanceText":"20 min subway","description":"The most iconic musical on Broadway. Defying Gravity is unforgettable.","tip":""},
    {"name":"Harry Potter and the Cursed Child","lat":40.7572,"lng":-73.9873,"category":"broadway","subcategory":"musical","starred":False,"address":"Lyric Theatre, 214 W 43rd St","distanceText":"20 min subway","description":"Mind-blowing stage magic and illusions. If you loved the HP Store, this is the next level.","tip":""},
    {"name":"Hadestown","lat":40.7601,"lng":-73.9870,"category":"broadway","subcategory":"musical","starred":False,"address":"Walter Kerr Theatre, 219 W 48th St","distanceText":"20 min subway","description":"Tony winner for Best Musical. Jazz-infused reimagined Greek myth. Deeply moving.","tip":""},
    # DC Cherry Blossoms
    {"name":"Tidal Basin","lat":38.8863,"lng":-77.0365,"category":"cherry-blossoms","subcategory":"viewing","starred":True,"address":"1501 Maine Ave SW, Washington DC","distanceText":"Near National Mall","description":"THE iconic cherry blossom spot. 3,000+ trees ringing the basin. Arrive by 7-8 AM to beat crowds. Peak bloom projected March 29-April 1.","tip":"Wear comfortable shoes — full loop is ~2 miles"},
    {"name":"East Potomac Park","lat":38.8723,"lng":-77.0289,"category":"cherry-blossoms","subcategory":"viewing","starred":True,"address":"Ohio Dr SW, Washington DC","distanceText":"South of Tidal Basin","description":"Less crowded alternative with 1,800+ cherry trees. Different varieties bloom earlier and later. Walking/biking path along Potomac is gorgeous.","tip":"Walk south from Tidal Basin"},
    {"name":"National Mall","lat":38.8899,"lng":-77.0229,"category":"cherry-blossoms","subcategory":"viewing","starred":False,"address":"National Mall, Washington DC","distanceText":"Central DC","description":"Cherry trees scattered throughout. Combine blossom viewing with monuments and museums — perfect for a full day.","tip":"Start at Capitol, walk west toward Lincoln Memorial"},
    {"name":"Dumbarton Oaks","lat":38.9146,"lng":-77.0629,"category":"cherry-blossoms","subcategory":"viewing","starred":False,"address":"1703 32nd St NW, Georgetown","distanceText":"Georgetown","description":"Beautiful private garden in Georgetown. Smaller, quieter, more curated. Cherry blossoms plus wisteria and spring blooms.","tip":"Open Tue-Sun 2-6 PM. $10 admission."},
    # DC Sightseeing
    {"name":"Lincoln Memorial","lat":38.8893,"lng":-77.0502,"category":"sightseeing","subcategory":"monuments","starred":True,"address":"2 Lincoln Memorial Cir NW, Washington DC","distanceText":"National Mall (west end)","description":"One of America's most powerful monuments. Go at sunrise or late evening — dramatically lit and almost empty.","tip":"Combine with nearby WWII, Korean War, and MLK memorials"},
    {"name":"WWII Memorial","lat":38.8894,"lng":-77.0405,"category":"sightseeing","subcategory":"monuments","starred":False,"address":"1750 Independence Ave SW, Washington DC","distanceText":"National Mall","description":"Beautiful open-air memorial. 56 pillars representing states and territories. Visit at night when it's lit up.","tip":"Open 24 hours"},
    {"name":"MLK Memorial","lat":38.8862,"lng":-77.0442,"category":"sightseeing","subcategory":"monuments","starred":False,"address":"1964 Independence Ave SW, Washington DC","distanceText":"Near Tidal Basin","description":"30-foot Stone of Hope sculpture. Located along Tidal Basin — combine with cherry blossom viewing.","tip":"Right next to Tidal Basin"},
    {"name":"Smithsonian Natural History","lat":38.8913,"lng":-77.0261,"category":"sightseeing","subcategory":"museums","starred":True,"address":"10th St & Constitution Ave NW, Washington DC","distanceText":"National Mall","description":"One of world's greatest museums — FREE. Hope Diamond, dinosaur hall, ocean exhibit. Could spend all day.","tip":"Free admission, open 10 AM-5:30 PM"},
    {"name":"Smithsonian Air & Space","lat":38.8882,"lng":-77.0199,"category":"sightseeing","subcategory":"museums","starred":True,"address":"600 Independence Ave SW, Washington DC","distanceText":"National Mall","description":"Wright Brothers Flyer, Apollo 11, Spirit of St. Louis. Recently renovated with stunning new exhibits. Free!","tip":"Free. Planetarium shows worth the extra fee."},
    {"name":"U.S. Capitol","lat":38.8897,"lng":-77.0089,"category":"sightseeing","subcategory":"monuments","starred":False,"address":"East Capitol St NE & First St SE, Washington DC","distanceText":"Capitol Hill","description":"The iconic dome. Free guided tours — book online. View west down the Mall from Capitol steps is the classic DC panorama.","tip":"Book free tour at visitthecapitol.gov"},
    {"name":"Library of Congress","lat":38.8887,"lng":-77.0047,"category":"sightseeing","subcategory":"museums","starred":False,"address":"101 Independence Ave SE, Washington DC","distanceText":"Capitol Hill","description":"Largest library in the world. Main Reading Room is breathtaking — ornate ceiling, three stories of books. Free and less crowded.","tip":"Free. Open Mon-Sat."},
    # DC Food
    {"name":"Rasika","lat":38.8965,"lng":-77.0194,"category":"food","subcategory":"indian","starred":True,"address":"633 D St NW, Washington DC","distanceText":"Penn Quarter, DC","description":"One of the best Indian restaurants in America. The palak chaat (crispy spinach) is legendary. Obama's favorite Indian restaurant in DC.","tip":"Reserve well in advance — books up fast"},
    {"name":"Bombay Street Food","lat":39.0826,"lng":-77.1536,"category":"food","subcategory":"indian","starred":True,"address":"4704 Dempsey St, Rockville, MD","distanceText":"30 min from DC","description":"Excellent chaat, pav bhaji, vada pav — authentic Bombay street food. Casual, affordable, great vegetarian options.","tip":"Casual counter-service. Everything is veg-friendly."},
    {"name":"Pappe","lat":38.9094,"lng":-77.0478,"category":"food","subcategory":"indian","starred":False,"address":"1367 Connecticut Ave NW, Washington DC","distanceText":"Dupont Circle, DC","description":"Modern Indian small plates in Dupont Circle. Inventive cocktails, lively atmosphere. Lamb seekh kebab and butter chicken are standouts.","tip":"Good for dinner after a day on the Mall"},
    {"name":"Woodlands","lat":38.9918,"lng":-76.9817,"category":"food","subcategory":"indian","starred":False,"address":"8046 New Hampshire Ave, Langley Park, MD","distanceText":"20 min from DC","description":"Authentic South Indian vegetarian. Dosas, idli, uttapam — the real deal. Pure vegetarian, Jain-friendly options available.","tip":"All vegetarian. Ask for Jain-friendly (no onion/garlic)."},
    {"name":"Heritage India","lat":38.9202,"lng":-77.0713,"category":"food","subcategory":"indian","starred":False,"address":"2400 Wisconsin Ave NW, Washington DC","distanceText":"Georgetown, DC","description":"Upscale Indian in Georgetown. Good vegetarian selection. Near Dumbarton Oaks — combine with cherry blossom garden visit.","tip":"Near Dumbarton Oaks"},
    # Gainesville VA
    {"name":"VOSAP Event","lat":38.7957,"lng":-77.6131,"category":"sightseeing","subcategory":"events","starred":True,"address":"Gainesville, VA","distanceText":"50 min from DC","description":"Voice of SAP event. Friday Mar 27 evening and Saturday Mar 28 from 3 PM onwards.","tip":"~50 min drive from DC. Plan cherry blossoms for morning before VOSAP at 3 PM."},
]

# Default center: apartment near Curry Hill/NoMad
DEFAULT_LAT = 40.7438
DEFAULT_LNG = -73.9927

def build_system_prompt(user_lat=None, user_lng=None):
    """Build the system prompt with all spot data for the chatbot."""
    location_context = ""
    if user_lat and user_lng:
        location_context = f"\n\nThe user's current location is: lat={user_lat}, lng={user_lng}. When recommending spots, prioritize those closest to their current location and mention approximate walking distance/time."
    
    spots_text = "\n".join([
        f"- {s['name']} ({s['category']}/{s['subcategory']}) at {s['address']} "
        f"[lat:{s['lat']}, lng:{s['lng']}] "
        f"{'⭐ VISHAL\'S PICK' if s['starred'] else ''} — "
        f"{s['description']}"
        f"{' TIP: ' + s['tip'] if s['tip'] else ''}"
        for s in SPOTS
    ])
    
    return f"""You are a warm, knowledgeable travel concierge helping Vishal's parents (Jayana & Naresh Shah) during their 12-day East Coast trip. Think of yourself as a local friend who knows NYC and DC inside and out — AND who knows their son's personal favorite spots.

YOUR STYLE:
- Talk like a friendly person, not a database. "Oh, you're near the Village? You HAVE to try Joe's Pizza — Vishal loves it" is way better than "Joe's Pizza is located at 7 Carmine St."
- Be enthusiastic about the starred (⭐) picks — these are Vishal's personal favorites. Say things like "This is one of Vishal's favorites!" or "Vishal specifically wanted you to try this one!"
- Give practical advice: "It's a 10 minute walk from your apartment" or "Take the F train, it's quick"
- If they seem hungry, suggest 2-3 options with different vibes (quick bite vs sit-down, familiar vs adventurous)
- Be concise but warm. 2-4 sentences per recommendation, 2-3 recommendations max per response.

HOW TO HANDLE REQUESTS:
1. FIRST check if Vishal's curated list has relevant spots. If yes, recommend those with a "Vishal recommends" callout.
2. If the list doesn't cover what they need, USE YOUR OWN KNOWLEDGE to help.
3. When recommending from general knowledge, clearly label it: "This isn't on Vishal's list, but a great option nearby is..."
4. You can mix: "Vishal's pick would be X, but if you want something different, Y is also great nearby."
5. For non-food questions (subway help, safety tips, weather, pharmacy, ATM, trains, etc.), just answer helpfully like any good local would.

TRIP OVERVIEW:
- Mar 20-24: NYC (home base: 101 W 24th St, Apt 24D, Chelsea/Flatiron)
- Mar 25: NJ — Swaminarayan (BAPS) temple visit
- Mar 26: Warren, NJ — Teji's house, Siddhachalam & Shrimad Rajchandra temples (rent a car)
- Mar 27: Train from Newark to DC — VOSAP event in Gainesville, VA (evening)
- Mar 28: Cherry blossoms (morning) + VOSAP from 3 PM
- Mar 29: Cherry blossoms (PEAK BLOOM projected Mar 29 - Apr 1!)
- Mar 30: Travel back to NJ
- Mar 31: Fly home EWR → LAX

CONTEXT:
- The family is Indian vegetarian. Vegetarian and vegan-friendly options are always appreciated
- HanGawi is fully vegan Korean, Jain-friendly (no onion, no garlic) — perfect for them
- GupShup and Bungalow are sister restaurants from Chef Vikas Khanna's team
- Curry Hill (Lex Ave, 26th-30th St) is a 5-10 min walk from the NYC apartment — great for familiar Indian food
- Rasika in DC is one of the best Indian restaurants in America — Obama's favorite
- For the NJ→DC leg: Amtrak Northeast Regional from Newark Penn to DC Union Station, ~3 hours, $50-90
- Cherry blossoms: Tidal Basin is THE iconic spot (go early AM), East Potomac Park is less crowded
- Gainesville, VA is ~50 min drive from DC
- They may ask about anything: restaurants, sightseeing, transit, cherry blossoms, temples, logistics. Help with ALL of it.
{location_context}

VISHAL'S CURATED SPOTS:
{spots_text}"""


def check_rate_limit(ip):
    """Simple rate limiter: max RATE_LIMIT requests per hour per IP."""
    now = time.time()
    key = hashlib.md5(ip.encode()).hexdigest()
    # Clean old entries
    rate_store[key] = [t for t in rate_store[key] if now - t < 3600]
    if len(rate_store[key]) >= RATE_LIMIT:
        return False
    rate_store[key].append(now)
    return True


@app.route("/")
def index():
    return render_template("index.html", spots=json.dumps(SPOTS))


@app.route("/chat", methods=["POST"])
def chat():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if not check_rate_limit(ip):
        return jsonify({"error": "Rate limit exceeded. Try again in a bit!"}), 429
    
    if not OPENAI_API_KEY:
        return jsonify({"error": "Chat is not configured."}), 500
    
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Please type a message!"}), 400
    if len(message) > 500:
        return jsonify({"error": "Message too long. Keep it under 500 characters."}), 400
    
    # Accept conversation history from frontend (last 20 messages max)
    history = data.get("history", [])
    if not isinstance(history, list):
        history = []
    history = history[-20:]  # Cap at 20 messages to control token usage
    
    user_lat = data.get("lat")
    user_lng = data.get("lng")
    
    system_prompt = build_system_prompt(user_lat, user_lng)
    
    # Build messages array: system + history + current message
    messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        role = h.get("role", "")
        content = h.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content[:500]})
    messages.append({"role": "user", "content": message})
    
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
            },
            timeout=15,
        )
        resp.raise_for_status()
        reply = resp.json()["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except requests.exceptions.Timeout:
        return jsonify({"error": "Took too long — try again!"}), 504
    except Exception as e:
        return jsonify({"error": "Something went wrong. Try again!"}), 500


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)

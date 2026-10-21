"""Seed command populating core Kiwi Trails database models.
Inserts default users categories guides tours images faqs departures and coupons.
Safe to rerun multiple times and supports full reset option.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.catalog.models import Category, Guide, Tour, TourFaq, TourImage, TourStatus
from apps.coupons.models import Coupon, CouponDiscountType
from apps.departures.models import Departure, DepartureStatus
from apps.seeds.constants import (
    COUPON_EXPIRED5,
    COUPON_ONEUSE,
    COUPON_SUMMER10,
    COUPON_SWITCHEDOFF,
    COUPON_WELCOME20,
)


class Command(BaseCommand):
    help = "Seed baseline Kiwi Trails database with users catalog departures and coupons"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing seed data before populating",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.reset_data()

        users_count = self.seed_users()
        categories_count = self.seed_categories()
        guides_count = self.seed_guides()
        tours_count, images_count, faqs_count = self.seed_catalog()
        departures_count = self.seed_departures()
        coupons_count = self.seed_coupons()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded core data: {users_count} users {categories_count} "
                f"categories {guides_count} guides {tours_count} tours {images_count} "
                f"images {faqs_count} faqs {departures_count} departures {coupons_count} coupons."
            )
        )

    def reset_data(self):
        Departure.objects.all().delete()
        TourFaq.objects.all().delete()
        TourImage.objects.all().delete()
        Tour.objects.all().delete()
        Category.objects.all().delete()
        Guide.objects.all().delete()
        Coupon.objects.all().delete()
        User.objects.filter(email__endswith="@kiwitrails.test").delete()

    def seed_users(self):
        users_data = [
            ("admin@kiwitrails.test", "Kiwi Admin", UserRole.ADMIN, "0211112222"),
            ("aroha@kiwitrails.test", "Aroha Smith", UserRole.CUSTOMER, "0212223333"),
            ("tane@kiwitrails.test", "Tane Williams", UserRole.CUSTOMER, "0213334444"),
            ("mei@kiwitrails.test", "Mei Chen", UserRole.CUSTOMER, "0214445555"),
            ("liam@kiwitrails.test", "Liam Taylor", UserRole.CUSTOMER, "0215556666"),
            ("sione@kiwitrails.test", "Sione Tupou", UserRole.CUSTOMER, "0216667777"),
        ]
        count = 0
        for email, full_name, role, phone in users_data:
            user = User.objects.filter(email=email).first()
            if not user:
                user = User(
                    email=email,
                    full_name=full_name,
                    role=role,
                    phone=phone,
                    is_active=True,
                )
                if role == UserRole.ADMIN:
                    user.is_superuser = True
                user.set_password("Password123!")
                user.save()
                count += 1
            else:
                user.full_name = full_name
                user.role = role
                user.phone = phone
                user.is_active = True
                if role == UserRole.ADMIN:
                    user.is_superuser = True
                user.set_password("Password123!")
                user.save()
                count += 1
        return count

    def seed_categories(self):
        category_names = ["Water", "Hiking", "Culture", "Wildlife", "Adventure"]
        count = 0
        for name in category_names:
            Category.objects.get_or_create(name=name)
            count += 1
        return count

    def seed_guides(self):
        guides_data = [
            (
                "Hemi Walker",
                "Born and raised in the central North Island Hemi brings over "
                "fifteen years "
                "of "
                "storytelling indigenous history and outdoor guiding experience.",
                "/media/seed/guides/hemi-walker.jpg",
                "English, Te Reo Māori",
            ),
            (
                "Sarah Jenkins",
                "Certified alpine hiking and sea kayaking instructor with a "
                "deep passion for "
                "New Zealand geological formations and conservation.",
                "/media/seed/guides/sarah-jenkins.jpg",
                "English, German",
            ),
            (
                "Rangi Bennett",
                "Marine biologist and naturalist specializing in southern "
                "marine mammals and "
                "fiordland wildlife along South Island coastlines.",
                "/media/seed/guides/rangi-bennett.jpg",
                "English, French",
            ),
        ]
        count = 0
        for full_name, bio, photo_url, languages in guides_data:
            guide = Guide.objects.filter(full_name=full_name).first()
            if not guide:
                Guide.objects.create(
                    full_name=full_name,
                    bio=bio,
                    photo_url=photo_url,
                    languages=languages,
                )
            else:
                guide.bio = bio
                guide.photo_url = photo_url
                guide.languages = languages
                guide.save()
            count += 1
        return count

    def get_tours_definition(self):
        return [
            {
                "title": "Taupō Lake Cruise",
                "description": (
                    "Scenic cruise on the sparkling waters of Lake Taupō visiting "
                    "the iconic "
                    "Mine Bay "
                    "Maori Rock Carvings. Includes morning tea commentary on "
                    "volcanic history "
                    "and "
                    "postcard perfect mountain views."
                ),
                "location": "Taupō",
                "category": "Water",
                "price": Decimal("249.00"),
                "duration": 1,
                "itinerary": (
                    "Morning departure from Taupō Boat Harbour. Cruise across "
                    "Lake Taupō towards "
                    "Mine Bay "
                    "to view the towering contemporary Maori Rock Carvings. Enjoy "
                    "fresh tea and "
                    "coffee with "
                    "volcanic commentary. Afternoon swimming stop in secluded "
                    "freshwater coves "
                    "before returning."
                ),
                "accessibility": (
                    "Wheelchair accessible lower deck and saloon. Accessible "
                    "boarding ramp at berth "
                    "4."
                ),
                "guidelines": (
                    "Please bring a windproof jacket sun hat and sunglasses. Flat "
                    "footwear "
                    "recommended."
                ),
                "meeting_point": "Taupō Boat Harbour Berth 4 Redoubt Street",
                "lat": Decimal("-38.689700"),
                "lng": Decimal("176.069400"),
                "guide": "Hemi Walker",
                "cancellation_days": 7,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/taupo-lake-cruise-1.jpg",
                        "Mine Bay Maori Rock Carvings on Lake Taupo",
                        1,
                    ),
                    (
                        "/media/seed/tours/taupo-lake-cruise-2.jpg",
                        "Catamaran cruising on Lake Taupo at sunset",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Are life jackets provided?",
                        "Yes life jackets in all adult and child sizes are provided onboard.",
                    ),
                    (
                        "Can we swim during the cruise?",
                        ("Yes during summer departures weather permitting there is a swim stop."),
                    ),
                ],
            },
            {
                "title": "Tongariro Alpine Crossing",
                "description": (
                    "Renowned as New Zealands greatest day walk across an active "
                    "volcanic "
                    "landscape. "
                    "Trek past Mount Ngauruhoe vibrant emerald lakes and steaming "
                    "geothermal "
                    "vents with an alpine guide."
                ),
                "location": "Tongariro",
                "category": "Hiking",
                "price": Decimal("185.00"),
                "duration": 1,
                "itinerary": (
                    "Early pickup from National Park Village. Ascend through "
                    "Mangatepopo Valley "
                    "towards the saddle. "
                    "Traverse South Crater and climb to Red Crater for sweeping "
                    "panoramas. "
                    "Descend past Emerald Lakes "
                    "and Blue Lake before continuing through native forest to Ketetahi."
                ),
                "accessibility": (
                    "Demanding high alpine mountain track. Not suitable for "
                    "wheelchairs or strollers."
                ),
                "guidelines": (
                    "Sturdy hiking boots thermal layers waterproof jacket minimum "
                    "2 litres water "
                    "required."
                ),
                "meeting_point": "Mangatepopo Carpark Tongariro National Park",
                "lat": Decimal("-39.144400"),
                "lng": Decimal("175.581000"),
                "guide": "Sarah Jenkins",
                "cancellation_days": 7,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/tongariro-crossing-1.jpg",
                        "Emerald Lakes in Tongariro National Park",
                        1,
                    ),
                    (
                        "/media/seed/tours/tongariro-crossing-2.jpg",
                        "Hikers crossing Red Crater on Tongariro track",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "What fitness level is needed?",
                        "A moderate to high level of cardiovascular fitness is required.",
                    ),
                    (
                        "What happens in adverse weather?",
                        ("If high winds or heavy rain create danger guides reroute or reschedule."),
                    ),
                ],
            },
            {
                "title": "Milford Sound Cruise",
                "description": (
                    "Journey deep into Fiordlands most celebrated fiord "
                    "surrounded by towering "
                    "granite cliffs "
                    "cascading waterfalls like Stirling Falls and basking New "
                    "Zealand fur seals."
                ),
                "location": "Milford Sound",
                "category": "Water",
                "price": Decimal("210.00"),
                "duration": 1,
                "itinerary": (
                    "Board your luxury catamaran at Milford Sound Visitor "
                    "Terminal. Cruise the "
                    "entire 16 kilometre "
                    "fiord out towards the Tasman Sea. Marvel at vertical granite "
                    "peaks. Stand "
                    "under Stirling Falls "
                    "mist and observe native fur seals basking on sea rocks."
                ),
                "accessibility": (
                    "Fully wheelchair accessible vessel with elevator access "
                    "between main passenger "
                    "decks."
                ),
                "guidelines": (
                    "Fiordland receives high rainfall. Bring a waterproof rain "
                    "jacket warm fleece and "
                    "camera."
                ),
                "meeting_point": "Milford Sound Visitor Terminal Highway 94",
                "lat": Decimal("-44.671500"),
                "lng": Decimal("167.926000"),
                "guide": "Rangi Bennett",
                "cancellation_days": 5,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/milford-sound-cruise-1.jpg",
                        "Mitre Peak rising over Milford Sound fiord",
                        1,
                    ),
                    (
                        "/media/seed/tours/milford-sound-cruise-2.jpg",
                        "Waterfall mist spraying tour boat in Milford Sound",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Is lunch included on the cruise?",
                        "Hot lunch and barista coffee are available for purchase onboard.",
                    ),
                    (
                        "Will we see wildlife on the fiord?",
                        ("Fur seals are resident year round and dolphins are frequently spotted."),
                    ),
                ],
            },
            {
                "title": "Waitomo Glowworm Caves",
                "description": (
                    "Glide silently in a boat through subterranean limestone "
                    "caverns illuminated "
                    "by thousands of "
                    "magical bioluminescent Arachnocampa luminosa glowworms overhead."
                ),
                "location": "Waitomo",
                "category": "Adventure",
                "price": Decimal("95.00"),
                "duration": 1,
                "itinerary": (
                    "Commence with a guided walking tour through dry limestone "
                    "chambers in the "
                    "Cathedral. Transfer "
                    "into silent wooden boats for a gentle glide across the "
                    "subterranean river "
                    "under glowing bioluminescence."
                ),
                "accessibility": (
                    "Cathedral chamber requires navigating stairs. Boat launch has stepped access."
                ),
                "guidelines": (
                    "Consistent underground temperature of 16 degrees Celsius. "
                    "Light sweater "
                    "recommended."
                ),
                "meeting_point": "Waitomo Caves Discovery Centre 39 Waitomo Village Road",
                "lat": Decimal("-38.261200"),
                "lng": Decimal("175.111000"),
                "guide": "Hemi Walker",
                "cancellation_days": 3,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/waitomo-glowworm-caves-1.jpg",
                        "Bioluminescent glowworms illuminating Waitomo cave ceiling",
                        1,
                    ),
                    (
                        "/media/seed/tours/waitomo-glowworm-caves-2.jpg",
                        "Limestone stalactites inside Waitomo Caves",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Is photography allowed inside?",
                        "Photography is strictly prohibited inside the glowworm grotto.",
                    ),
                    (
                        "How long is the underground boat ride?",
                        "The peaceful boat ride lasts approximately twenty minutes.",
                    ),
                ],
            },
            {
                "title": "Rotorua Māori Cultural Evening",
                "description": (
                    "An authentic cultural immersion featuring a traditional "
                    "powhiri welcome "
                    "ceremony mesmerizing kapa haka "
                    "performance warrior waka on the sacred spring and a "
                    "delicious hangi feast "
                    "cooked underground."
                ),
                "location": "Rotorua",
                "category": "Culture",
                "price": Decimal("160.00"),
                "duration": 1,
                "itinerary": (
                    "Arrive at the traditional village clearing for a formal "
                    "powhiri welcome "
                    "ceremony and warrior challenge. "
                    "Enter the meeting house for songs poi dances and the haka. "
                    "Conclude with an "
                    "authentic hangi buffet feast."
                ),
                "accessibility": (
                    "Paved pathways throughout village grounds and accessible dining area."
                ),
                "guidelines": (
                    "Please remove footwear when entering the meeting house. "
                    "Modest casual attire "
                    "appropriate."
                ),
                "meeting_point": "Mitai Maori Village 196 Fairy Springs Road Rotorua",
                "lat": Decimal("-38.109800"),
                "lng": Decimal("176.223500"),
                "guide": "Hemi Walker",
                "cancellation_days": 5,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/rotorua-maori-culture-1.jpg",
                        "Traditional Maori kapa haka performance in Rotorua",
                        1,
                    ),
                    (
                        "/media/seed/tours/rotorua-maori-culture-2.jpg",
                        "Traditional hangi earthen pit oven feast in Rotorua",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Are dietary requirements accommodated?",
                        "Vegetarian vegan and gluten free options are clearly labelled.",
                    ),
                    (
                        "Is transport available from central Rotorua?",
                        ("Complimentary return coach transfers from central hotels are provided."),
                    ),
                ],
            },
            {
                "title": "Abel Tasman Kayaking",
                "description": (
                    "Paddle along the golden beaches granite headlands and calm "
                    "turquoise "
                    "lagoons of Abel Tasman National Park. "
                    "Spot playful seal pups at Adele Island wildlife sanctuary."
                ),
                "location": "Abel Tasman",
                "category": "Water",
                "price": Decimal("175.00"),
                "duration": 1,
                "itinerary": (
                    "Safety briefing on golden Kaiteriteri beach. Launch double "
                    "sea kayaks and "
                    "paddle north past Split Apple "
                    "Rock into Adele Island marine sanctuary. Stop on a golden "
                    "sand beach for "
                    "lunch before gentle paddle back."
                ),
                "accessibility": ("Requires sitting upright in kayak and upper body coordination."),
                "guidelines": (
                    "Bring swimwear towel sun cream water bottle and quick dry "
                    "shorts. Dry bags "
                    "supplied."
                ),
                "meeting_point": "Kaiteriteri Beachfront Kaiteriteri",
                "lat": Decimal("-41.039000"),
                "lng": Decimal("173.018000"),
                "guide": "Sarah Jenkins",
                "cancellation_days": 5,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/abel-tasman-kayaking-1.jpg",
                        "Sea kayakers along Abel Tasman golden beach",
                        1,
                    ),
                    (
                        "/media/seed/tours/abel-tasman-kayaking-2.jpg",
                        "Pristine turquoise lagoon in Abel Tasman National Park",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Do I need previous kayaking experience?",
                        "No experience necessary. Double kayaks are exceptionally stable.",
                    ),
                    (
                        "What is the minimum age for kayaking?",
                        ("The minimum age for the day kayak tour is twelve years with an adult."),
                    ),
                ],
            },
            {
                "title": "Matamata Film Set Tour",
                "description": (
                    "Step into the whimsical world of Middle earth at the "
                    "authentic Hobbiton "
                    "Movie Set. "
                    "Wander lush farmland past colorful Hobbit holes the Mill and "
                    "finish with a "
                    "beverage at the Green Dragon Inn."
                ),
                "location": "Matamata",
                "category": "Culture",
                "price": Decimal("120.00"),
                "duration": 1,
                "itinerary": (
                    "Board the tour coach at The Shires Rest for a scenic drive. "
                    "Guided walking "
                    "tour through the 12 acre "
                    "movie set visiting 44 unique Hobbit Holes and finishing at "
                    "The Green Dragon "
                    "Inn for a beverage."
                ),
                "accessibility": (
                    "Tour follows unpaved dirt pathways. Golf cart assistance "
                    "available with advance "
                    "booking."
                ),
                "guidelines": (
                    "Comfortable walking shoes and rain jackets recommended. "
                    "Bring camera for iconic "
                    "photo stops."
                ),
                "meeting_point": "The Shires Rest 501 Buckland Road Hinuera Matamata",
                "lat": Decimal("-37.872000"),
                "lng": Decimal("175.683000"),
                "guide": "Sarah Jenkins",
                "cancellation_days": 3,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/matamata-film-set-1.jpg",
                        "Hobbit hole with round green door at Matamata movie set",
                        1,
                    ),
                    (
                        "/media/seed/tours/matamata-film-set-2.jpg",
                        "The Green Dragon Inn across the lake in Hobbiton",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Can we enter inside the Hobbit holes?",
                        ("Yes guests can step inside specially constructed interior Hobbit holes."),
                    ),
                    (
                        "Is the beverage at Green Dragon included?",
                        ("Yes one complimentary traditional beverage is included for each guest."),
                    ),
                ],
            },
            {
                "title": "Kaikōura Whale Watch",
                "description": (
                    "Encounter the magnificent Giant Sperm Whale up close off the rugged "
                    "Kaikōura coast where deep undersea "
                    "trenches create a rich marine mammal haven. Also see dusky "
                    "dolphins and "
                    "albatross."
                ),
                "location": "Kaikōura",
                "category": "Wildlife",
                "price": Decimal("165.00"),
                "duration": 1,
                "itinerary": (
                    "Check in at Whaleway Station and board modern hydrofoil "
                    "catamarans. Cruise "
                    "out to the Kaikoura "
                    "undersea canyon. Tour guides use hydrophones to locate "
                    "clicking Sperm "
                    "Whales as they surface to breathe."
                ),
                "accessibility": (
                    "Vessel features wide interior aisles and wheelchair tie down "
                    "bays on main saloon "
                    "deck."
                ),
                "guidelines": (
                    "Open sea swells can occur. Motion sickness medication taken "
                    "one hour prior is "
                    "recommended."
                ),
                "meeting_point": "The Whaleway Station Kaikoura",
                "lat": Decimal("-42.411000"),
                "lng": Decimal("173.681000"),
                "guide": "Rangi Bennett",
                "cancellation_days": 3,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/kaikoura-whale-watch-1.jpg",
                        "Sperm whale tail fluking against Kaikoura mountains",
                        1,
                    ),
                    (
                        "/media/seed/tours/kaikoura-whale-watch-2.jpg",
                        "Pod of dusky dolphins swimming off Kaikoura coast",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "What is the success rate for whale sightings?",
                        (
                            "Whale Watch Kaikoura maintains an approximate ninety five "
                            "percent sighting "
                            "rate."
                        ),
                    ),
                    (
                        "What if no whales are seen?",
                        (
                            "If your tour does not encounter a whale an eighty percent "
                            "refund is "
                            "provided."
                        ),
                    ),
                ],
            },
            {
                "title": "Mount Cook & Hooker Valley Track",
                "description": (
                    "Walk across three picturesque suspension bridges over "
                    "roaring alpine rivers "
                    "with panoramic views of "
                    "Aoraki Mount Cook ending at the iceberg dotted Hooker Glacier lake."
                ),
                "location": "Mount Cook",
                "category": "Hiking",
                "price": Decimal("195.00"),
                "duration": 1,
                "itinerary": (
                    "Meet guide at White Horse Hill campground. Embark on the 10 "
                    "kilometre "
                    "return trail across three suspension "
                    "bridges. Enjoy close up views of Mount Sefton and Aoraki Mount Cook "
                    "arriving at iceberg dotted Hooker Lake."
                ),
                "accessibility": (
                    "Well graded gravel trail and timber boardwalks throughout. "
                    "Wheelchair access to "
                    "first bridge."
                ),
                "guidelines": (
                    "Alpine weather shifts rapidly. Carry thermal layers "
                    "windbreaker hat and water "
                    "bottle."
                ),
                "meeting_point": "White Horse Hill Campground Hooker Valley Road",
                "lat": Decimal("-43.719000"),
                "lng": Decimal("170.093000"),
                "guide": "Sarah Jenkins",
                "cancellation_days": 5,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/mount-cook-hooker-valley-1.jpg",
                        "Hooker Valley swing bridge with Aoraki Mount Cook backdrop",
                        1,
                    ),
                    (
                        "/media/seed/tours/mount-cook-hooker-valley-2.jpg",
                        "Floating icebergs in Hooker Glacier lake Mount Cook",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Is this track suitable for children?",
                        "Yes the track is relatively flat and suitable for active children.",
                    ),
                    (
                        "Are trekking poles provided?",
                        (
                            "Trekking poles are available upon request from your guide at "
                            "the trailhead."
                        ),
                    ),
                ],
            },
            {
                "title": "Franz Josef Glacier Valley Walk",
                "description": (
                    "Guided valley trek through temperate rainforest into the "
                    "dramatic glacial "
                    "retreat zone of Franz Josef. "
                    "Learn about glaciology and rapid landscape change."
                ),
                "location": "Franz Josef",
                "category": "Adventure",
                "price": Decimal("145.00"),
                "duration": 1,
                "itinerary": (
                    "Equip with rain gear at glacier base. Walk through lush "
                    "rainforest moraine "
                    "onto the raw riverbed. "
                    "Follow your glaciologist guide to safe viewing platforms "
                    "directly facing "
                    "the blue terminal ice face."
                ),
                "accessibility": (
                    "Trail involves walking on uneven rocky riverbed terrain. Not "
                    "suitable for "
                    "wheelchairs."
                ),
                "guidelines": (
                    "Sturdy enclosed walking shoes with good tread required. "
                    "Heavy rain jackets "
                    "provided."
                ),
                "meeting_point": "Glacier Base Cron Street Franz Josef Village",
                "lat": Decimal("-43.388000"),
                "lng": Decimal("170.183000"),
                "guide": "Rangi Bennett",
                "cancellation_days": 3,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/franz-josef-glacier-1.jpg",
                        "Franz Josef Glacier terminal ice face and valley",
                        1,
                    ),
                    (
                        "/media/seed/tours/franz-josef-glacier-2.jpg",
                        "Glacial river carving through Franz Josef valley moraine",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Do we actually walk on the ice?",
                        (
                            "This valley trail takes you to the safest viewpoint facing "
                            "the terminal ice "
                            "face."
                        ),
                    ),
                    (
                        "Why has the glacier changed shape?",
                        (
                            "Franz Josef is dynamic and responds rapidly to changing "
                            "climate and "
                            "rainfall patterns."
                        ),
                    ),
                ],
            },
            {
                "title": "Queenstown Shotover Jet & Canyon Adventure",
                "description": (
                    "The worlds most thrilling jet boat ride skimming across "
                    "shallow river "
                    "waters and navigating narrow "
                    "towering canyons with full 360 degree spins."
                ),
                "location": "Queenstown",
                "category": "Adventure",
                "price": Decimal("179.00"),
                "duration": 1,
                "itinerary": (
                    "Transfer to Shotover River base at Arthurs Point. Put on "
                    "life jacket and "
                    "protective splash coat. "
                    "Board the twin engine jet boat for high octane thrills "
                    "through narrow rock "
                    "canyons with 360 spins."
                ),
                "accessibility": (
                    "Passengers must be able to sit securely and brace with arms "
                    "during high speed "
                    "maneuvers."
                ),
                "guidelines": (
                    "Minimum height of 100 centimetres required. Eyeglasses "
                    "should be secured with "
                    "straps."
                ),
                "meeting_point": "Shotover Jet Beach Arthurs Point Queenstown",
                "lat": Decimal("-44.985000"),
                "lng": Decimal("168.675000"),
                "guide": "Sarah Jenkins",
                "cancellation_days": 2,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/queenstown-shotover-jet-1.jpg",
                        "Red Shotover jet boat speeding through narrow canyon walls",
                        1,
                    ),
                    (
                        "/media/seed/tours/queenstown-shotover-jet-2.jpg",
                        "Thrilling 360 degree spin on Shotover River Queenstown",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Will I get wet on the jet boat?",
                        (
                            "Expect water spray especially during full spins. Splash "
                            "coats are provided."
                        ),
                    ),
                    (
                        "Is the jet boat safe in narrow canyons?",
                        (
                            "Shotover Jet has carried millions of passengers with world "
                            "class safety "
                            "standards."
                        ),
                    ),
                ],
            },
            {
                "title": "Bay of Islands Dolphin Cruise & Hole in the Rock",
                "description": (
                    "Cruise through subtropical island sanctuaries out to Cape "
                    "Brett and steer "
                    "through the iconic Hole in the Rock. "
                    "Look for bottlenose dolphins and seabirds along the route."
                ),
                "location": "Bay of Islands",
                "category": "Wildlife",
                "price": Decimal("155.00"),
                "duration": 1,
                "itinerary": (
                    "Depart Paihia Wharf cruising past Russell through 144 "
                    "subtropical islands. "
                    "Look for wild dolphins "
                    "from observation decks. Pass Cape Brett lighthouse before "
                    "skipper navigates "
                    "through Hole in the Rock."
                ),
                "accessibility": (
                    "Catamaran has ramp boarding at Paihia and accessible lower deck saloon."
                ),
                "guidelines": (
                    "Bring sun protection binoculars and light jacket for the "
                    "outer coastal breezes."
                ),
                "meeting_point": "Paihia Wharf Marsden Road Paihia",
                "lat": Decimal("-35.281800"),
                "lng": Decimal("174.091500"),
                "guide": "Hemi Walker",
                "cancellation_days": 3,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/bay-of-islands-cruise-1.jpg",
                        "Catamaran passing through Hole in the Rock at Cape Brett",
                        1,
                    ),
                    (
                        "/media/seed/tours/bay-of-islands-cruise-2.jpg",
                        "Dolphins jumping beside cruise boat in Bay of Islands",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Can we swim with the dolphins?",
                        (
                            "To protect marine mammal conservation guidelines this is a "
                            "viewing only "
                            "experience."
                        ),
                    ),
                    (
                        "Does the boat always go through the hole?",
                        (
                            "Navigating through the hole depends on calm sea swell "
                            "conditions on the "
                            "day."
                        ),
                    ),
                ],
            },
            {
                "title": "Coromandel Cathedral Cove Coastal Walk",
                "description": (
                    "Coastal trail along pohutukawa fringed cliffs descending to "
                    "the world "
                    "famous natural limestone arch of "
                    "Cathedral Cove Te Whanganui A Hei marine reserve."
                ),
                "location": "Coromandel",
                "category": "Hiking",
                "price": Decimal("135.00"),
                "duration": 1,
                "itinerary": (
                    "Begin walk from Hahei village overlook following coastal "
                    "cliff trail "
                    "through native trees. Enjoy panoramic "
                    "views over Mercury Bay before descending steps to Cathedral "
                    "Cove white sand "
                    "beach."
                ),
                "accessibility": (
                    "Walk involves paved paths concluding with timber steps to "
                    "beach. Not wheelchair "
                    "accessible."
                ),
                "guidelines": (
                    "Wear comfortable walking shoes bring swimwear beach towel and drinking water."
                ),
                "meeting_point": "Hahei Visitor Carpark Hahei Beach Road Coromandel",
                "lat": Decimal("-36.839000"),
                "lng": Decimal("175.803000"),
                "guide": "Rangi Bennett",
                "cancellation_days": 3,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/coromandel-cathedral-cove-1.jpg",
                        "Cathedral Cove natural limestone archway onto white sand beach",
                        1,
                    ),
                    (
                        "/media/seed/tours/coromandel-cathedral-cove-2.jpg",
                        "Pohutukawa blooms along Coromandel coastal cliff path",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "How long is the walk to Cathedral Cove?",
                        (
                            "The scenic walk takes approximately forty five minutes each "
                            "way at a steady "
                            "pace."
                        ),
                    ),
                    (
                        "Is swimming safe at Cathedral Cove?",
                        (
                            "Yes the beach has gentle waters ideal for swimming though no "
                            "lifeguards are "
                            "present."
                        ),
                    ),
                ],
            },
            {
                "title": "Te Puia Geothermal Valley & Pōhutu Geyser",
                "description": (
                    "Marvel at the southern hemispheres largest active geyser "
                    "Pōhutu erupting up "
                    "to 30 metres high. "
                    "Visit the national carving and weaving schools and the Kiwi "
                    "Conservation "
                    "Centre."
                ),
                "location": "Rotorua",
                "category": "Culture",
                "price": Decimal("110.00"),
                "duration": 1,
                "itinerary": (
                    "Explore Te Whakarewarewa thermal valley home to the famous "
                    "Pohutu Geyser. "
                    "Visit the New Zealand Maori "
                    "Arts and Crafts Institute to observe master carvers. Walk "
                    "through nocturnal "
                    "kiwi house."
                ),
                "accessibility": (
                    "Extensive network of sealed flat pathways and wheelchair "
                    "accessible viewing "
                    "platforms."
                ),
                "guidelines": (
                    "Stay strictly on designated boardwalks and paths due to high "
                    "geothermal ground "
                    "temperatures."
                ),
                "meeting_point": "Te Puia Welcome Centre Hemo Road Rotorua",
                "lat": Decimal("-38.161000"),
                "lng": Decimal("176.249000"),
                "guide": "Hemi Walker",
                "cancellation_days": 3,
                "status": TourStatus.ACTIVE,
                "images": [
                    (
                        "/media/seed/tours/te-puia-geothermal-1.jpg",
                        "Pohutu Geyser erupting with steam plumes at Te Puia",
                        1,
                    ),
                    (
                        "/media/seed/tours/te-puia-geothermal-2.jpg",
                        "Traditional wood carving master craftsman at Te Puia",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "How often does Pohutu Geyser erupt?",
                        (
                            "Pohutu is the most active geyser in New Zealand erupting "
                            "once or twice "
                            "every hour."
                        ),
                    ),
                    (
                        "Can we take photos in the Kiwi house?",
                        (
                            "Flash photography is strictly prohibited inside the "
                            "nocturnal kiwi house."
                        ),
                    ),
                ],
            },
            {
                "title": "Fiordland Wilderness Expedition",
                "description": (
                    "Multi day remote expedition traversing Dusky Sound and "
                    "Doubtful Sound with "
                    "bushcraft immersion and heritage ecology. "
                    "Archived expedition tour for testing."
                ),
                "location": "Fiordland",
                "category": "Adventure",
                "price": Decimal("450.00"),
                "duration": 3,
                "itinerary": (
                    "Three day wilderness expedition deep into pristine Fiordland "
                    "backcountry "
                    "and secluded sounds. "
                    "Features bushcraft immersion helicopter transfer to Dusky "
                    "Sound and native "
                    "bird conservation trails."
                ),
                "accessibility": (
                    "Demanding backcountry wilderness trek. High physical fitness essential."
                ),
                "guidelines": (
                    "Full alpine tramping gear sleeping bag and waterproof layers required."
                ),
                "meeting_point": "Te Anau Lakefront Visitor Centre Lakefront Drive",
                "lat": Decimal("-45.416000"),
                "lng": Decimal("167.712000"),
                "guide": "Rangi Bennett",
                "cancellation_days": 14,
                "status": TourStatus.ARCHIVED,
                "images": [
                    (
                        "/media/seed/tours/fiordland-wilderness-1.jpg",
                        "Misty mountains and deep fjords of Doubtful Sound",
                        1,
                    ),
                    (
                        "/media/seed/tours/fiordland-wilderness-2.jpg",
                        "Dense moss and native beech forest in Fiordland National Park",
                        2,
                    ),
                ],
                "faqs": [
                    (
                        "Is this expedition currently operating?",
                        "This expedition is currently archived for seasonal testing.",
                    ),
                    (
                        "What is the group size?",
                        (
                            "Expeditions are strictly capped at eight explorers to "
                            "minimize ecological "
                            "footprint."
                        ),
                    ),
                ],
            },
        ]

    def seed_catalog(self):
        tours_def = self.get_tours_definition()
        tours_count = 0
        images_count = 0
        faqs_count = 0

        for item in tours_def:
            category = Category.objects.get(name=item["category"])
            guide = Guide.objects.filter(full_name=item["guide"]).first()

            tour = Tour.objects.filter(title=item["title"]).first()
            if not tour:
                tour = Tour.objects.create(
                    title=item["title"],
                    description=item["description"],
                    location=item["location"],
                    category=category,
                    price_per_person=item["price"],
                    duration_days=item["duration"],
                    itinerary=item["itinerary"],
                    accessibility_info=item["accessibility"],
                    visitor_guidelines=item["guidelines"],
                    meeting_point_name=item["meeting_point"],
                    meeting_lat=item["lat"],
                    meeting_lng=item["lng"],
                    guide=guide,
                    cancellation_days=item["cancellation_days"],
                    status=item["status"],
                )
            else:
                tour.description = item["description"]
                tour.location = item["location"]
                tour.category = category
                tour.price_per_person = item["price"]
                tour.duration_days = item["duration"]
                tour.itinerary = item["itinerary"]
                tour.accessibility_info = item["accessibility"]
                tour.visitor_guidelines = item["guidelines"]
                tour.meeting_point_name = item["meeting_point"]
                tour.meeting_lat = item["lat"]
                tour.meeting_lng = item["lng"]
                tour.guide = guide
                tour.cancellation_days = item["cancellation_days"]
                tour.status = item["status"]
                tour.save()
            tours_count += 1

            for img_url, alt, order in item["images"]:
                img = TourImage.objects.filter(tour=tour, sort_order=order).first()
                if not img:
                    TourImage.objects.create(
                        tour=tour,
                        image_url=img_url,
                        alt_text=alt,
                        sort_order=order,
                    )
                else:
                    img.image_url = img_url
                    img.alt_text = alt
                    img.save()
                images_count += 1

            for q, a in item["faqs"]:
                faq = TourFaq.objects.filter(tour=tour, question=q).first()
                if not faq:
                    TourFaq.objects.create(
                        tour=tour,
                        question=q,
                        answer=a,
                        sort_order=1,
                    )
                else:
                    faq.answer = a
                    faq.save()
                faqs_count += 1

        return tours_count, images_count, faqs_count

    def seed_departures(self):
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        active_tours = Tour.objects.filter(status=TourStatus.ACTIVE)
        count = 0

        for tour in active_tours:
            past_start = now - timedelta(days=14)
            past_deadline = now - timedelta(days=21)
            past_dep = Departure.objects.filter(
                tour=tour,
                status=DepartureStatus.COMPLETED,
            ).first()
            if not past_dep:
                Departure.objects.create(
                    tour=tour,
                    start_datetime=past_start,
                    capacity=20,
                    booking_deadline=past_deadline,
                    status=DepartureStatus.COMPLETED,
                )
            else:
                past_dep.capacity = 20
                past_dep.booking_deadline = past_deadline
                past_dep.save()
            count += 1

            f1_start = now + timedelta(days=14)
            f1_deadline = now + timedelta(days=7)
            f2_start = now + timedelta(days=28)
            f2_deadline = now + timedelta(days=21)

            sched_deps = list(
                Departure.objects.filter(
                    tour=tour,
                    status=DepartureStatus.SCHEDULED,
                    capacity=20,
                ).order_by("id")
            )
            if len(sched_deps) == 0:
                Departure.objects.create(
                    tour=tour,
                    start_datetime=f1_start,
                    capacity=20,
                    booking_deadline=f1_deadline,
                    status=DepartureStatus.SCHEDULED,
                )
                Departure.objects.create(
                    tour=tour,
                    start_datetime=f2_start,
                    capacity=20,
                    booking_deadline=f2_deadline,
                    status=DepartureStatus.SCHEDULED,
                )
            elif len(sched_deps) == 1:
                Departure.objects.create(
                    tour=tour,
                    start_datetime=f2_start,
                    capacity=20,
                    booking_deadline=f2_deadline,
                    status=DepartureStatus.SCHEDULED,
                )
            count += 2

        taupo_tour = Tour.objects.get(title="Taupō Lake Cruise")
        cancelled_start = now + timedelta(days=20)
        cancelled_deadline = now + timedelta(days=13)
        cancelled_dep = Departure.objects.filter(
            tour=taupo_tour,
            status=DepartureStatus.CANCELLED,
        ).first()
        if not cancelled_dep:
            Departure.objects.create(
                tour=taupo_tour,
                start_datetime=cancelled_start,
                capacity=15,
                booking_deadline=cancelled_deadline,
                status=DepartureStatus.CANCELLED,
            )
        count += 1

        tongariro_tour = Tour.objects.get(title="Tongariro Alpine Crossing")
        full_start = now + timedelta(days=10)
        full_deadline = now + timedelta(days=3)
        full_dep = Departure.objects.filter(
            tour=tongariro_tour,
            capacity=4,
            status=DepartureStatus.SCHEDULED,
        ).first()
        if not full_dep:
            Departure.objects.create(
                tour=tongariro_tour,
                start_datetime=full_start,
                capacity=4,
                booking_deadline=full_deadline,
                status=DepartureStatus.SCHEDULED,
            )
        count += 1

        milford_tour = Tour.objects.get(title="Milford Sound Cruise")
        closed_start = now + timedelta(days=2)
        closed_deadline = now - timedelta(days=1)
        closed_dep = Departure.objects.filter(
            tour=milford_tour,
            capacity=16,
            status=DepartureStatus.SCHEDULED,
        ).first()
        if not closed_dep:
            Departure.objects.create(
                tour=milford_tour,
                start_datetime=closed_start,
                capacity=16,
                booking_deadline=closed_deadline,
                status=DepartureStatus.SCHEDULED,
            )
        count += 1

        return count

    def seed_coupons(self):
        now = timezone.now()
        coupons_data = [
            (
                COUPON_SUMMER10,
                CouponDiscountType.PERCENT,
                Decimal("10.00"),
                now + timedelta(days=90),
                100,
                0,
                True,
            ),
            (
                COUPON_WELCOME20,
                CouponDiscountType.FIXED,
                Decimal("20.00"),
                now + timedelta(days=90),
                100,
                0,
                True,
            ),
            (
                COUPON_EXPIRED5,
                CouponDiscountType.PERCENT,
                Decimal("5.00"),
                now - timedelta(days=10),
                100,
                0,
                True,
            ),
            (
                COUPON_SWITCHEDOFF,
                CouponDiscountType.PERCENT,
                Decimal("15.00"),
                now + timedelta(days=90),
                100,
                0,
                False,
            ),
            (
                COUPON_ONEUSE,
                CouponDiscountType.FIXED,
                Decimal("15.00"),
                now + timedelta(days=90),
                1,
                1,
                True,
            ),
        ]
        count = 0
        for code, dtype, val, expires, max_u, used, active in coupons_data:
            Coupon.objects.update_or_create(
                code=code,
                defaults={
                    "discount_type": dtype,
                    "discount_value": val,
                    "expires_at": expires,
                    "max_uses": max_u,
                    "times_used": used,
                    "is_active": active,
                },
            )
            count += 1
        return count

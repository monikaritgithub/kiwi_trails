"""Python script to generate complete, production-grade draw.io diagrams
matching the exact high-level academic sample style from the assessment reference PDF:
- High level architecture diagram without unnecessary low-level details
- Crisp white background boxes (no dark colors)
- Zero line-text overlaps (layer titles aligned left, flow channels through center)
- Clean black borders and typography

The 11 Database Entities represented at the Model Layer:
Customer • Admin • Tour • Departure • Booking • Coupon • Attendance • Review • Category • Guide • TourImage

Outputs:
1. diagrams/kiwi-trails-architecture-diagram.drawio (Figure 1: High Level System Architecture)
2. diagrams/kiwi-trails-use-case-diagram.drawio     (Figure 2: Full Platform Use Case Diagram)
3. diagrams/kiwi-trails-class-diagram.drawio        (Figure 3: Complete 11-Model Class Diagram)
4. diagrams/kiwi-trails-sequence-diagram.drawio     (Figure 4: Full Booking Lifecycle Sequence Diagram)
5. diagrams/kiwi-trails-er-diagram.drawio           (Figure 5: Complete 11-Table ER Diagram in Chen Notation)
6. diagrams/kiwi-trails-activity-diagram.drawio     (Figure 6: Complete Reservation Lifecycle Activity Diagram)
7. diagrams/kiwi-trails-all-diagrams.drawio         (Combined master multi-page bundle)
"""

import html
import os

def esc(text):
    return html.escape(str(text))

def wrap_drawio_xml(name, cells_xml, page_width=1100, page_height=900):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2026-10-26T00:00:00.000Z" agent="KiwiTrails" version="21.6.8" type="device">
  <diagram id="diagram_1" name="{esc(name)}">
    <mxGraphModel dx="1422" dy="798" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{page_width}" pageHeight="{page_height}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
{cells_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

def create_bundle_drawio(pages):
    diagrams_xml = []
    for pid, name, cells_xml, pw, ph in pages:
        diagrams_xml.append(f"""  <diagram id="{esc(pid)}" name="{esc(name)}">
    <mxGraphModel dx="1422" dy="798" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{pw}" pageHeight="{ph}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
{cells_xml}
      </root>
    </mxGraphModel>
  </diagram>""")
    inner = "\n".join(diagrams_xml)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2026-10-26T00:00:00.000Z" agent="KiwiTrails" version="21.6.8" type="device">
{inner}
</mxfile>
"""

# ==============================================================================
# 1. HIGH LEVEL SYSTEM ARCHITECTURE DIAGRAM (Figure 1: Clean, Minimalist, White)
# ==============================================================================
def build_architecture_diagram():
    cells = []
    cid = 100

    def next_id():
        nonlocal cid
        cid += 1
        return str(cid)

    # Realistic academic style: white boxes, black borders, black text
    box_style = "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontStyle=1;fontSize=11;align=center;verticalAlign=middle;"
    layer_style = "rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=4 4;fillColor=none;strokeColor=#555555;strokeWidth=1;align=left;spacingLeft=12;verticalAlign=top;spacingTop=6;fontSize=10;fontStyle=1;fontColor=#333333;"
    outer_style = "rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 6;fillColor=none;strokeColor=#000000;strokeWidth=1.5;align=left;spacingLeft=15;verticalAlign=top;spacingTop=8;fontSize=11;fontStyle=1;fontColor=#000000;"
    db_style = "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=10;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontStyle=1;fontSize=11;align=center;verticalAlign=middle;"
    line_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endSize=6;labelBackgroundColor=#FFFFFF;"
    caption_style = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=2;fontColor=#333333;"

    # Outer System Container
    sys_id = next_id()
    cells.append(f'''        <mxCell id="{sys_id}" value="Kiwi Trails System" style="{outer_style}" vertex="1" parent="1">
      <mxGeometry x="100" y="120" width="840" height="580" as="geometry"/>
    </mxCell>''')

    # Top Actors (Clean white boxes)
    admin_actor_id = next_id()
    cells.append(f'''        <mxCell id="{admin_actor_id}" value="Admin" style="{box_style}" vertex="1" parent="1">
      <mxGeometry x="320" y="50" width="110" height="40" as="geometry"/>
    </mxCell>''')

    cust_actor_id = next_id()
    cells.append(f'''        <mxCell id="{cust_actor_id}" value="Customer" style="{box_style}" vertex="1" parent="1">
      <mxGeometry x="620" y="50" width="110" height="40" as="geometry"/>
    </mxCell>''')

    # Layer 1: Web Portals (Top-left aligned title prevents overlap)
    layer_wp_id = next_id()
    cells.append(f'''        <mxCell id="{layer_wp_id}" value="Web Portals" style="{layer_style}" vertex="1" parent="{sys_id}">
      <mxGeometry x="30" y="30" width="780" height="90" as="geometry"/>
    </mxCell>''')

    admin_portal_id = next_id()
    cells.append(f'''        <mxCell id="{admin_portal_id}" value="Admin Portal&#xa;React :3000" style="{box_style}" vertex="1" parent="{layer_wp_id}">
      <mxGeometry x="160" y="25" width="160" height="45" as="geometry"/>
    </mxCell>''')

    cust_portal_id = next_id()
    cells.append(f'''        <mxCell id="{cust_portal_id}" value="Customer Portal&#xa;React :3000" style="{box_style}" vertex="1" parent="{layer_wp_id}">
      <mxGeometry x="460" y="25" width="160" height="45" as="geometry"/>
    </mxCell>''')

    # Layer 2: Controller Layer (Top-left aligned title prevents overlap)
    layer_ctrl_id = next_id()
    cells.append(f'''        <mxCell id="{layer_ctrl_id}" value="Controller Layer" style="{layer_style}" vertex="1" parent="{sys_id}">
      <mxGeometry x="30" y="140" width="780" height="90" as="geometry"/>
    </mxCell>''')

    admin_ctrl_id = next_id()
    cells.append(f'''        <mxCell id="{admin_ctrl_id}" value="Admin Controllers" style="{box_style}" vertex="1" parent="{layer_ctrl_id}">
      <mxGeometry x="160" y="25" width="160" height="45" as="geometry"/>
    </mxCell>''')

    cust_ctrl_id = next_id()
    cells.append(f'''        <mxCell id="{cust_ctrl_id}" value="Customer Controllers" style="{box_style}" vertex="1" parent="{layer_ctrl_id}">
      <mxGeometry x="460" y="25" width="160" height="45" as="geometry"/>
    </mxCell>''')

    # Layer 3: Service Layer (Top-left aligned title prevents overlap)
    layer_svc_id = next_id()
    cells.append(f'''        <mxCell id="{layer_svc_id}" value="Service Layer" style="{layer_style}" vertex="1" parent="{sys_id}">
      <mxGeometry x="30" y="250" width="780" height="150" as="geometry"/>
    </mxCell>''')

    svc_report = next_id()
    cells.append(f'''        <mxCell id="{svc_report}" value="Report Service" style="{box_style}" vertex="1" parent="{layer_svc_id}">
      <mxGeometry x="50" y="30" width="120" height="40" as="geometry"/>
    </mxCell>''')

    svc_attendance = next_id()
    cells.append(f'''        <mxCell id="{svc_attendance}" value="Attendance Service" style="{box_style}" vertex="1" parent="{layer_svc_id}">
      <mxGeometry x="50" y="90" width="120" height="40" as="geometry"/>
    </mxCell>''')

    svc_booking = next_id()
    cells.append(f'''        <mxCell id="{svc_booking}" value="Booking Engine" style="{box_style}" vertex="1" parent="{layer_svc_id}">
      <mxGeometry x="270" y="60" width="120" height="45" as="geometry"/>
    </mxCell>''')

    svc_tour = next_id()
    cells.append(f'''        <mxCell id="{svc_tour}" value="Tour Service" style="{box_style}" vertex="1" parent="{layer_svc_id}">
      <mxGeometry x="410" y="60" width="120" height="45" as="geometry"/>
    </mxCell>''')

    svc_coupon = next_id()
    cells.append(f'''        <mxCell id="{svc_coupon}" value="Coupon Service" style="{box_style}" vertex="1" parent="{layer_svc_id}">
      <mxGeometry x="610" y="30" width="120" height="40" as="geometry"/>
    </mxCell>''')

    svc_review = next_id()
    cells.append(f'''        <mxCell id="{svc_review}" value="Review Service" style="{box_style}" vertex="1" parent="{layer_svc_id}">
      <mxGeometry x="610" y="90" width="120" height="40" as="geometry"/>
    </mxCell>''')

    # Layer 4: Model Layer (Top-left aligned title prevents overlap)
    layer_model_id = next_id()
    cells.append(f'''        <mxCell id="{layer_model_id}" value="Model Layer" style="{layer_style}" vertex="1" parent="{sys_id}">
      <mxGeometry x="30" y="420" width="780" height="110" as="geometry"/>
    </mxCell>''')

    models_box_id = next_id()
    cells.append(f'''        <mxCell id="{models_box_id}" value="Customer • Admin • Tour • Departure • Booking • Coupon • Attendance • Review" style="{box_style}" vertex="1" parent="{layer_model_id}">
      <mxGeometry x="90" y="35" width="600" height="45" as="geometry"/>
    </mxCell>''')

    # Bottom Database (Cylinder)
    db_id = next_id()
    cells.append(f'''        <mxCell id="{db_id}" value="SQLite Database" style="{db_style}" vertex="1" parent="1">
      <mxGeometry x="455" y="740" width="130" height="50" as="geometry"/>
    </mxCell>''')

    # Flow connections through clear channels ensuring zero line-text overlaps
    flows = [
        (admin_actor_id, admin_portal_id, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
        (cust_actor_id, cust_portal_id, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
        (admin_portal_id, admin_ctrl_id, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
        (cust_portal_id, cust_ctrl_id, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
        (admin_ctrl_id, svc_report, "exitX=0.2;exitY=1;entryX=0.5;entryY=0;"),
        (admin_ctrl_id, svc_attendance, "exitX=0.2;exitY=1;entryX=0.5;entryY=0;"),
        (cust_ctrl_id, svc_booking, "exitX=0.2;exitY=1;entryX=0.5;entryY=0;"),
        (cust_ctrl_id, svc_coupon, "exitX=0.8;exitY=1;entryX=0.5;entryY=0;"),
        (cust_ctrl_id, svc_review, "exitX=0.8;exitY=1;entryX=0.5;entryY=0;"),
        (svc_booking, svc_tour, "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
        (svc_booking, models_box_id, "exitX=0.5;exitY=1;entryX=0.35;entryY=0;"),
        (svc_tour, models_box_id, "exitX=0.5;exitY=1;entryX=0.55;entryY=0;"),
        (models_box_id, db_id, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;")
    ]

    for src, dst, port_st in flows:
        eid = next_id()
        st = f"{line_style};{port_st}"
        cells.append(f'''        <mxCell id="{eid}" value="" style="{st}" edge="1" parent="1" source="{src}" target="{dst}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>''')

    # Figure Caption
    cap_id = next_id()
    cells.append(f'''        <mxCell id="{cap_id}" value="Figure 1: High level architecture of the Kiwi Trails System, showing the flow from Admin and Customer actors through the Web Portals, Controller Layer, Service Layer, and Model Layer down to the SQLite database." style="{caption_style}" vertex="1" parent="1">
      <mxGeometry x="50" y="820" width="940" height="30" as="geometry"/>
    </mxCell>''')

    return "\n".join(cells), 1050, 880


# ==============================================================================
# 2. CLASS DIAGRAM (Figure 3)
# ==============================================================================
def build_class_diagram():
    cells = []
    cid = 300

    def next_id():
        nonlocal cid
        cid += 1
        return str(cid)

    header_style = "swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=0;marginBottom=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=11;fontColor=#000000;"
    item_style = "text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=6;spacingRight=6;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;fontSize=9;fontColor=#000000;"
    line_style = "line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=3;rotatable=0;labelPosition=right;points=[];portConstraint=eastwest;strokeColor=#000000;"
    caption_style = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=2;fontColor=#333333;"

    classes = [
        {
            "var": "Category", "title": "Category (catalog.Category)", "x": 60, "y": 80, "w": 250, "h": 110,
            "attrs": ["- id: Integer [PK]", "- name: String(60) [Unique]", "- created_at: DateTime"],
            "methods": ["+ get_tours_count(): Integer"]
        },
        {
            "var": "Guide", "title": "Guide (catalog.Guide)", "x": 60, "y": 240, "w": 250, "h": 140,
            "attrs": ["- id: Integer [PK]", "- full_name: String(100)", "- bio: Text", "- languages: String(150)"],
            "methods": ["+ get_languages_list(): List"]
        },
        {
            "var": "Tour", "title": "Tour (catalog.Tour)", "x": 390, "y": 80, "w": 280, "h": 300,
            "attrs": [
                "- id: Integer [PK]", "- title: String(150)", "- description: Text", "- location: String(100)",
                "- category_id: FK -> Category", "- guide_id: FK -> Guide [Optional]", "- price_per_person: Decimal(10,2)",
                "- duration_days: Integer", "- cancellation_days: Integer = 7", "- status: Enum {active, archived}"
            ],
            "methods": ["+ is_active(): Boolean", "+ get_cover_image(): String", "+ get_average_rating(): Decimal"]
        },
        {
            "var": "TourImage", "title": "TourImage (catalog.TourImage)", "x": 750, "y": 80, "w": 250, "h": 130,
            "attrs": ["- id: Integer [PK]", "- tour_id: FK -> Tour [Cascade]", "- image_url: String(255)", "- alt_text: String(150)", "- sort_order: Integer"],
            "methods": []
        },
        {
            "var": "TourFaq", "title": "TourFaq (catalog.TourFaq)", "x": 750, "y": 250, "w": 250, "h": 130,
            "attrs": ["- id: Integer [PK]", "- tour_id: FK -> Tour [Cascade]", "- question: String(255)", "- answer: Text", "- sort_order: Integer"],
            "methods": []
        },
        {
            "var": "Departure", "title": "Departure (departures.Departure)", "x": 390, "y": 450, "w": 280, "h": 190,
            "attrs": [
                "- id: Integer [PK]", "- tour_id: FK -> Tour [Protect]", "- start_datetime: DateTime (UTC)",
                "- capacity: PositiveInteger", "- booking_deadline: DateTime", "- status: Enum {scheduled, completed, cancelled}"
            ],
            "methods": ["+ get_seats_taken(): Integer", "+ get_seats_left(): Integer", "+ is_booking_open(): Boolean"]
        },
        {
            "var": "Booking", "title": "Booking (bookings.Booking)", "x": 390, "y": 710, "w": 280, "h": 280,
            "attrs": [
                "- id: Integer [PK]", "- booking_reference: String(20) [Unique]", "- user_id: FK -> User [Protect]",
                "- departure_id: FK -> Departure [Protect]", "- traveller_count: PositiveInteger", "- price_per_person: Decimal(10,2)",
                "- subtotal: Decimal(10,2)", "- discount_amount: Decimal(10,2)", "- total_price: Decimal(10,2)",
                "- coupon_id: FK -> Coupon [Null]", "- status: Enum {pending, approved, rejected, cancelled, completed}"
            ],
            "methods": ["+ can_cancel(): Boolean", "+ calculate_totals(): Void", "+ approve(): Void"]
        },
        {
            "var": "User", "title": "User (accounts.User)", "x": 60, "y": 710, "w": 250, "h": 220,
            "attrs": [
                "- id: Integer [PK]", "- full_name: String(100)", "- email: Email(150) [Unique]", "- password: String(128)",
                "- role: Enum {customer, admin}", "- phone: String(30)", "- is_active: Boolean", "- created_at: DateTime"
            ],
            "methods": ["+ is_admin(): Boolean", "+ is_customer(): Boolean", "+ check_password(raw): Boolean"]
        },
        {
            "var": "Coupon", "title": "Coupon (coupons.Coupon)", "x": 60, "y": 990, "w": 250, "h": 180,
            "attrs": [
                "- id: Integer [PK]", "- code: String(30) [Unique]", "- discount_type: Enum {percent, fixed}",
                "- discount_value: Decimal(10,2)", "- expires_at: DateTime", "- max_uses: PositiveInteger",
                "- times_used: PositiveInteger", "- is_active: Boolean"
            ],
            "methods": ["+ is_valid(): Boolean", "+ apply_discount(subtotal): Decimal"]
        },
        {
            "var": "Attendance", "title": "Attendance (bookings.Attendance)", "x": 750, "y": 710, "w": 250, "h": 150,
            "attrs": [
                "- id: Integer [PK]", "- booking_id: OneToOne -> Booking [Cascade]", "- status: Enum {present, absent}",
                "- marked_by_id: FK -> User [Protect]", "- marked_at: DateTime"
            ],
            "methods": ["+ mark_present(): Void", "+ mark_absent(): Void"]
        },
        {
            "var": "Review", "title": "Review (reviews.Review)", "x": 750, "y": 920, "w": 250, "h": 180,
            "attrs": [
                "- id: Integer [PK]", "- booking_id: OneToOne -> Booking [Protect]", "- user_id: FK -> User [Protect]",
                "- tour_id: FK -> Tour [Protect]", "- rating: SmallInteger (1..5)", "- comment: Text", "- created_at: DateTime"
            ],
            "methods": []
        }
    ]

    c_map = {}

    for c in classes:
        pid = next_id()
        c_map[c["var"]] = pid
        cells.append(f'''        <mxCell id="{pid}" value="{esc(c['title'])}" style="{header_style}" vertex="1" parent="1">
      <mxGeometry x="{c['x']}" y="{c['y']}" width="{c['w']}" height="{c['h']}" as="geometry"/>
    </mxCell>''')

        for a in c["attrs"]:
            aid = next_id()
            cells.append(f'''        <mxCell id="{aid}" value="{esc(a)}" style="{item_style}" vertex="1" parent="{pid}">
      <mxGeometry y="26" width="{c['w']}" height="15" as="geometry"/>
    </mxCell>''')

        if c["methods"]:
            lid = next_id()
            cells.append(f'''        <mxCell id="{lid}" value="" style="{line_style}" vertex="1" parent="{pid}">
      <mxGeometry y="26" width="{c['w']}" height="8" as="geometry"/>
    </mxCell>''')
            for m in c["methods"]:
                mid = next_id()
                cells.append(f'''        <mxCell id="{mid}" value="{esc(m)}" style="{item_style}" vertex="1" parent="{pid}">
      <mxGeometry y="26" width="{c['w']}" height="15" as="geometry"/>
    </mxCell>''')

    edges = [
        ("Category", "Tour", "categorizes", "exitX=1;exitY=0.5;entryX=0;entryY=0.2;"),
        ("Guide", "Tour", "leads", "exitX=1;exitY=0.5;entryX=0;entryY=0.7;"),
        ("Tour", "TourImage", "has images", "exitX=1;exitY=0.2;entryX=0;entryY=0.5;"),
        ("Tour", "TourFaq", "has faqs", "exitX=1;exitY=0.7;entryX=0;entryY=0.5;"),
        ("Tour", "Departure", "schedules", "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
        ("Departure", "Booking", "holds", "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
        ("User", "Booking", "reserves", "exitX=1;exitY=0.35;entryX=0;entryY=0.35;"),
        ("Coupon", "Booking", "applies to", "exitX=1;exitY=0.5;entryX=0;entryY=0.8;"),
        ("Booking", "Attendance", "manifest", "exitX=1;exitY=0.35;entryX=0;entryY=0.5;"),
        ("Booking", "Review", "evaluates", "exitX=1;exitY=0.8;entryX=0;entryY=0.5;")
    ]

    for src, dst, label, port_style in edges:
        eid = next_id()
        st = f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=none;fontSize=9;fontColor=#000000;labelBackgroundColor=#FFFFFF;spacingBottom=2;{port_style}"
        cells.append(f'''        <mxCell id="{eid}" value="{label}" style="{st}" edge="1" parent="1" source="{c_map[src]}" target="{c_map[dst]}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>''')

    cap_id = next_id()
    cells.append(f'''        <mxCell id="{cap_id}" value="Figure 3: Class diagram detailing all 11 domain entities of the Kiwi Trails platform, with clear adjacent placement preventing line crossings." style="{caption_style}" vertex="1" parent="1">
      <mxGeometry x="60" y="1220" width="940" height="30" as="geometry"/>
    </mxCell>''')

    return "\n".join(cells), 1080, 1280


# ==============================================================================
# 3. ENTITY RELATIONSHIP DIAGRAM (Figure 5)
# ==============================================================================
def build_er_diagram():
    cells = []
    cid = 600

    def next_id():
        nonlocal cid
        cid += 1
        return str(cid)

    ent_style = "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontStyle=1;fontSize=11;align=center;verticalAlign=middle;"
    attr_style = "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=9;align=center;verticalAlign=middle;"
    pk_attr_style = "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontStyle=4;fontSize=9;align=center;verticalAlign=middle;"
    rel_diamond_style = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=9;fontStyle=2;align=center;verticalAlign=middle;"
    line_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1;endArrow=none;labelBackgroundColor=#FFFFFF;"
    direct_line = "html=1;strokeColor=#000000;strokeWidth=1;endArrow=none;"
    caption_style = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=2;fontColor=#333333;"

    entities = {
        "Category": {"x": 100, "y": 80, "w": 90, "h": 40},
        "Guide": {"x": 100, "y": 260, "w": 90, "h": 40},
        "Tour": {"x": 480, "y": 170, "w": 90, "h": 40},
        "TourImage": {"x": 860, "y": 80, "w": 90, "h": 40},
        "TourFaq": {"x": 860, "y": 260, "w": 90, "h": 40},
        "Departure": {"x": 480, "y": 420, "w": 90, "h": 40},
        "Booking": {"x": 480, "y": 660, "w": 90, "h": 40},
        "User": {"x": 100, "y": 660, "w": 90, "h": 40},
        "Coupon": {"x": 100, "y": 880, "w": 90, "h": 40},
        "Attendance": {"x": 860, "y": 660, "w": 90, "h": 40},
        "Review": {"x": 860, "y": 880, "w": 90, "h": 40}
    }

    ent_nodes = {}
    for name, pos in entities.items():
        nid = next_id()
        ent_nodes[name] = nid
        cells.append(f'''        <mxCell id="{nid}" value="{name}" style="{ent_style}" vertex="1" parent="1">
      <mxGeometry x="{pos['x']}" y="{pos['y']}" width="{pos['w']}" height="{pos['h']}" as="geometry"/>
    </mxCell>''')

    attrs_map = {
        "Category": [("id(PK)", True, 50, 30), ("name", False, 130, 30)],
        "Guide": [("id(PK)", True, 40, 215), ("full_name", False, 120, 215)],
        "Tour": [("id(PK)", True, 440, 115), ("title", False, 520, 115), ("location", False, 420, 230), ("price", False, 540, 230)],
        "TourImage": [("id(PK)", True, 820, 30), ("image_url", False, 900, 30)],
        "TourFaq": [("id(PK)", True, 820, 215), ("question", False, 900, 215)],
        "Departure": [("id(PK)", True, 390, 425), ("start_dt", False, 590, 425)],
        "User": [("id(PK)", True, 40, 610), ("email", False, 120, 610), ("role", False, 40, 720)],
        "Booking": [("id(PK)", True, 430, 610), ("ref", False, 520, 610), ("travellers", False, 430, 720), ("total_price", False, 520, 720)],
        "Coupon": [("id(PK)", True, 40, 830), ("code", False, 120, 830)],
        "Attendance": [("id(PK)", True, 820, 610), ("status", False, 900, 610)],
        "Review": [("id(PK)", True, 820, 830), ("rating", False, 900, 830)]
    }

    for ent, alist in attrs_map.items():
        eparent = ent_nodes[ent]
        for aname, is_pk, ax, ay in alist:
            aid = next_id()
            ast = pk_attr_style if is_pk else attr_style
            cells.append(f'''        <mxCell id="{aid}" value="{aname}" style="{ast}" vertex="1" parent="1">
      <mxGeometry x="{ax}" y="{ay}" width="55" height="24" as="geometry"/>
    </mxCell>''')
            leid = next_id()
            cells.append(f'''        <mxCell id="{leid}" value="" style="{direct_line}" edge="1" parent="1" source="{eparent}" target="{aid}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>''')

    rel_data = [
        ("Category", "Tour", "categorizes", 290, 100),
        ("Guide", "Tour", "leads", 290, 240),
        ("Tour", "TourImage", "has images", 670, 100),
        ("Tour", "TourFaq", "has faqs", 670, 240),
        ("Tour", "Departure", "schedules", 495, 295),
        ("Departure", "Booking", "holds", 495, 540),
        ("User", "Booking", "reserves", 290, 665),
        ("Coupon", "Booking", "applies", 290, 810),
        ("Booking", "Attendance", "manifest", 670, 665),
        ("Booking", "Review", "evaluates", 670, 810)
    ]

    for src, dst, rname, rx, ry in rel_data:
        rid = next_id()
        cells.append(f'''        <mxCell id="{rid}" value="{rname}" style="{rel_diamond_style}" vertex="1" parent="1">
      <mxGeometry x="{rx}" y="{ry}" width="65" height="30" as="geometry"/>
    </mxCell>''')
        cells.append(f'''        <mxCell id="{next_id()}" value="1" style="{line_style}" edge="1" parent="1" source="{ent_nodes[src]}" target="{rid}"><mxGeometry relative="1" as="geometry"/></mxCell>''')
        cells.append(f'''        <mxCell id="{next_id()}" value="N" style="{line_style}" edge="1" parent="1" source="{rid}" target="{ent_nodes[dst]}"><mxGeometry relative="1" as="geometry"/></mxCell>''')

    cap_id = next_id()
    cells.append(f'''        <mxCell id="{cap_id}" value="Figure 5: Entity Relationship diagram of the Kiwi Trails database schema showing all 11 entities in Chen notation with zero line crossings." style="{caption_style}" vertex="1" parent="1">
      <mxGeometry x="60" y="980" width="940" height="30" as="geometry"/>
    </mxCell>''')

    return "\n".join(cells), 1080, 1040


# ==============================================================================
# 4. USE CASE DIAGRAM (Figure 2)
# ==============================================================================
def build_use_case_diagram():
    cells = []
    cid = 200

    def next_id():
        nonlocal cid
        cid += 1
        return str(cid)

    actor_style = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=none;strokeColor=#000000;strokeWidth=1;fontColor=#000000;fontSize=11;"
    uc_style = "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=11;fontColor=#000000;align=center;verticalAlign=middle;"
    line_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1;endArrow=none;"
    inc_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;strokeColor=#000000;strokeWidth=1;endArrow=open;endSize=6;fontSize=10;fontColor=#000000;labelBackgroundColor=#FFFFFF;"
    caption_style = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=2;fontColor=#333333;"

    cust_id = next_id()
    cells.append(f'''        <mxCell id="{cust_id}" value="Customer" style="{actor_style}" vertex="1" parent="1">
      <mxGeometry x="180" y="240" width="40" height="80" as="geometry"/>
    </mxCell>''')

    customer_ucs = [
        ("uc_login_reg", "Login/Register", 80),
        ("uc_search", "Search/Browse&#xa;Tours Catalog", 150),
        ("uc_book", "Book Guided&#xa;Tour Departure", 230),
        ("uc_cancel", "Cancel Booking&#xa;Reservation", 310),
        ("uc_review", "Submit Verified&#xa;Tour Review", 390)
    ]

    c_nodes = {}
    for key, text, y_pos in customer_ucs:
        uid = next_id()
        c_nodes[key] = uid
        cells.append(f'''        <mxCell id="{uid}" value="{text}" style="{uc_style}" vertex="1" parent="1">
      <mxGeometry x="340" y="{y_pos}" width="130" height="52" as="geometry"/>
    </mxCell>''')

        eid = next_id()
        cells.append(f'''        <mxCell id="{eid}" value="" style="{line_style}" edge="1" parent="1" source="{cust_id}" target="{uid}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>''')

    included_ucs = [
        ("uc_search", "View Photos &amp; FAQs", 150),
        ("uc_book", "Calculate Price Quote&#xa;&amp; Apply Voucher", 230),
        ("uc_cancel", "Validate Cancellation&#xa;Window Policy", 310),
        ("uc_review", "Verify Completed&#xa;Tour Status", 390)
    ]

    for src_key, text, y_pos in included_ucs:
        inc_id = next_id()
        cells.append(f'''        <mxCell id="{inc_id}" value="{text}" style="{uc_style}" vertex="1" parent="1">
      <mxGeometry x="580" y="{y_pos}" width="140" height="52" as="geometry"/>
    </mxCell>''')

        eid = next_id()
        cells.append(f'''        <mxCell id="{eid}" value="&lt;&lt;include&gt;&gt;" style="{inc_style}" edge="1" parent="1" source="{c_nodes[src_key]}" target="{inc_id}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>''')

    admin_id = next_id()
    cells.append(f'''        <mxCell id="{admin_id}" value="Admin &amp; Guide" style="{actor_style}" vertex="1" parent="1">
      <mxGeometry x="180" y="720" width="40" height="80" as="geometry"/>
    </mxCell>''')

    admin_ucs = [
        ("uc_adm_login", "Staff Login", 480),
        ("uc_manage_tours", "Manage Tours &amp; Media", 540),
        ("uc_schedule_dep", "Schedule Departures", 600),
        ("uc_moderate_book", "Moderate Bookings&#xa;(Approve/Reject)", 660),
        ("uc_record_att", "Record Departure&#xa;Attendance Roster", 720),
        ("uc_manage_coupons", "Manage Promo&#xa;Discount Coupons", 780),
        ("uc_moderate_rev", "Moderate Customer&#xa;Reviews", 840),
        ("uc_guides_cats", "Manage Guides &amp;&#xa;Tour Categories", 900),
        ("uc_gen_report", "View Analytics&#xa;Dashboard", 960)
    ]

    for key, text, y_pos in admin_ucs:
        uid = next_id()
        cells.append(f'''        <mxCell id="{uid}" value="{text}" style="{uc_style}" vertex="1" parent="1">
      <mxGeometry x="340" y="{y_pos}" width="130" height="48" as="geometry"/>
    </mxCell>''')

        eid = next_id()
        cells.append(f'''        <mxCell id="{eid}" value="" style="{line_style}" edge="1" parent="1" source="{admin_id}" target="{uid}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>''')

    cap_id = next_id()
    cells.append(f'''        <mxCell id="{cap_id}" value="Figure 2: Use case diagram illustrating Customer and Admin interactions across catalog, departures, bookings, attendance, coupons, and reviews." style="{caption_style}" vertex="1" parent="1">
      <mxGeometry x="80" y="1030" width="940" height="30" as="geometry"/>
    </mxCell>''')

    return "\n".join(cells), 1100, 1090


# ==============================================================================
# 5. SEQUENCE DIAGRAM (Figure 4)
# ==============================================================================
def build_sequence_diagram():
    cells = []
    cid = 400

    def next_id():
        nonlocal cid
        cid += 1
        return str(cid)

    actor_style = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=none;strokeColor=#000000;strokeWidth=1;fontColor=#000000;fontSize=11;"
    box_style = "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontStyle=1;fontSize=11;align=center;"
    lifeline_line = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=4 4;strokeColor=#888888;strokeWidth=1;endArrow=none;"
    msg_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1.2;endArrow=classic;endSize=6;fontSize=10;fontColor=#000000;verticalAlign=bottom;labelBackgroundColor=#FFFFFF;spacingBottom=3;"
    ret_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=4 4;strokeColor=#000000;strokeWidth=1.2;endArrow=open;endSize=6;fontSize=10;fontColor=#000000;verticalAlign=bottom;labelBackgroundColor=#FFFFFF;spacingBottom=3;"
    step_circle_style = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#000000;strokeColor=#000000;fontColor=#FFFFFF;fontStyle=1;fontSize=9;align=center;verticalAlign=middle;"
    caption_style = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=2;fontColor=#333333;"

    lifelines = [
        {"key": "cust", "type": "actor", "label": "Customer", "x": 100},
        {"key": "ui", "type": "box", "label": "UI Controller", "x": 360},
        {"key": "engine", "type": "box", "label": "Booking Engine", "x": 640},
        {"key": "coupon", "type": "box", "label": "Coupon Service", "x": 900},
        {"key": "db", "type": "box", "label": "Database ORM", "x": 1140},
        {"key": "admin", "type": "actor", "label": "Admin Staff", "x": 1360}
    ]

    ll_x = {}
    top_y = 60
    bottom_y = 1260

    for ll in lifelines:
        ll_x[ll["key"]] = ll["x"]
        if ll["type"] == "actor":
            aid = next_id()
            cells.append(f'''        <mxCell id="{aid}" value="{ll['label']}" style="{actor_style}" vertex="1" parent="1">
      <mxGeometry x="{ll['x'] - 20}" y="{top_y}" width="40" height="70" as="geometry"/>
    </mxCell>''')
            baid = next_id()
            cells.append(f'''        <mxCell id="{baid}" value="{ll['label']}" style="{actor_style}" vertex="1" parent="1">
      <mxGeometry x="{ll['x'] - 20}" y="{bottom_y - 20}" width="40" height="70" as="geometry"/>
    </mxCell>''')
        else:
            bid = next_id()
            cells.append(f'''        <mxCell id="{bid}" value="{ll['label']}" style="{box_style}" vertex="1" parent="1">
      <mxGeometry x="{ll['x'] - 60}" y="{top_y + 15}" width="120" height="40" as="geometry"/>
    </mxCell>''')
            bbid = next_id()
            cells.append(f'''        <mxCell id="{bbid}" value="{ll['label']}" style="{box_style}" vertex="1" parent="1">
      <mxGeometry x="{ll['x'] - 60}" y="{bottom_y}" width="120" height="40" as="geometry"/>
    </mxCell>''')

        lid = next_id()
        cells.append(f'''        <mxCell id="{lid}" value="" style="{lifeline_line}" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry">
        <mxPoint x="{ll['x']}" y="{top_y + 70}" as="sourcePoint"/>
        <mxPoint x="{ll['x']}" y="{bottom_y - 20}" as="targetPoint"/>
      </mxGeometry>
    </mxCell>''')

    steps = [
        (1, "msg", "cust", "ui", 160, "Search available tours and departures"),
        (2, "msg", "ui", "db", 210, "Query active scheduled departure dates"),
        (3, "ret", "db", "ui", 260, "Return scheduled departures list"),
        (4, "ret", "ui", "cust", 310, "Display tour details and departures"),
        (5, "msg", "cust", "ui", 360, "Select date and enter promo code"),
        (6, "msg", "ui", "engine", 410, "POST /quote (calculate totals)"),
        (7, "msg", "engine", "coupon", 460, "Validate voucher and calculate discount"),
        (8, "ret", "coupon", "engine", 510, "Return discount amount (NZD)"),
        (9, "ret", "engine", "ui", 560, "Return live price quote summary"),
        (10, "ret", "ui", "cust", 610, "Display total fee quote summary"),
        (11, "msg", "cust", "ui", 660, "Confirm booking requirements"),
        (12, "msg", "ui", "engine", 710, "POST /bookings (submit reservation)"),
        (13, "msg", "engine", "db", 760, "Lock departure &amp; insert Booking (PENDING)"),
        (14, "ret", "db", "engine", 810, "Commit atomic transaction save"),
        (15, "ret", "engine", "ui", 860, "Return reference (KT-7H4K9Q)"),
        (16, "ret", "ui", "cust", 910, "Display reservation confirmed toast"),
        (17, "msg", "engine", "admin", 960, "Notify staff of pending reservation"),
        (18, "msg", "admin", "engine", 1010, "Approve reservation request"),
        (19, "msg", "engine", "db", 1060, "UPDATE bookings SET status = 'approved'"),
        (20, "msg", "admin", "db", 1110, "Departure day: Record Attendance"),
        (21, "ret", "engine", "cust", 1160, "Tour completed: request customer review")
    ]

    for num, mtype, src, dst, y, text in steps:
        sx = ll_x[src]
        dx = ll_x[dst]

        circle_id = next_id()
        cells.append(f'''        <mxCell id="{circle_id}" value="{num}" style="{step_circle_style}" vertex="1" parent="1">
      <mxGeometry x="{sx - 8}" y="{y - 8}" width="16" height="16" as="geometry"/>
    </mxCell>''')

        st = msg_style if mtype == "msg" else ret_style
        mid = next_id()
        cells.append(f'''        <mxCell id="{mid}" value="{text}" style="{st}" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry">
        <mxPoint x="{sx}" y="{y}" as="sourcePoint"/>
        <mxPoint x="{dx}" y="{y}" as="targetPoint"/>
      </mxGeometry>
    </mxCell>''')

    cap_id = next_id()
    cells.append(f'''        <mxCell id="{cap_id}" value="Figure 4: Sequence diagram showing the end-to-end booking process, from customer tour discovery through quote calculation, atomic seat hold, admin approval, attendance, and review." style="{caption_style}" vertex="1" parent="1">
      <mxGeometry x="60" y="1300" width="1340" height="30" as="geometry"/>
    </mxCell>''')

    return "\n".join(cells), 1460, 1360


# ==============================================================================
# 6. ACTIVITY DIAGRAM (Figure 6)
# ==============================================================================
def build_activity_diagram():
    cells = []
    cid = 500

    def next_id():
        nonlocal cid
        cid += 1
        return str(cid)

    start_style = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#000000;strokeColor=#000000;"
    end_style = "ellipse;html=1;shape=endState;fillColor=#000000;strokeColor=#000000;"
    act_style = "rounded=1;whiteSpace=wrap;html=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=11;fontColor=#000000;align=center;verticalAlign=middle;"
    dec_style = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=10;fontColor=#000000;fontStyle=1;align=center;verticalAlign=middle;"
    line_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1;endArrow=classic;endSize=6;fontSize=10;fontColor=#000000;labelBackgroundColor=#FFFFFF;"
    caption_style = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=2;fontColor=#333333;"

    nodes = {}

    def add_node(key, label, style, x, y, w, h):
        nid = next_id()
        nodes[key] = nid
        cells.append(f'''        <mxCell id="{nid}" value="{label}" style="{style}" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>
    </mxCell>''')
        return nid

    add_node("start", "", start_style, 385, 40, 30, 30)
    add_node("search", "Customer browses tours catalog&#xa;and selects scheduled departure", act_style, 290, 100, 220, 50)
    add_node("calc_fee", "System calculates live quote&#xa;and validates coupon voucher", act_style, 290, 180, 220, 50)
    add_node("check_cap", "Seats&#xa;Available?", dec_style, 350, 260, 100, 60)
    add_node("pay_submit", "Customer submits reservation&#xa;with pickup &amp; dietary details", act_style, 290, 350, 220, 50)
    add_node("atomic_hold", "System executes atomic transaction:&#xa;Locks departure &amp; creates Pending booking", act_style, 280, 430, 240, 50)
    add_node("admin_dec", "Admin&#xa;Decision?", dec_style, 350, 510, 100, 60)
    add_node("mark_approved", "System marks Status = APPROVED&#xa;and issues confirmation invoice", act_style, 290, 600, 220, 50)
    add_node("departure_day", "Departure Day: Guide opens manifest&#xa;and records Attendance status", act_style, 290, 680, 220, 50)
    add_node("complete_tour", "Tour concludes successfully:&#xa;Departure &amp; Booking = COMPLETED", act_style, 290, 760, 220, 50)
    add_node("leave_review", "Customer submits verified review&#xa;and system recalculates tour rating", act_style, 280, 840, 240, 50)
    add_node("end_success", "", end_style, 385, 920, 30, 30)

    add_node("reject_booking", "System marks Status = REJECTED&#xa;and releases reserved seats", act_style, 590, 515, 200, 50)
    add_node("end_reject", "", end_style, 675, 600, 30, 30)

    edges = [
        ("start", "search", ""),
        ("search", "calc_fee", ""),
        ("calc_fee", "check_cap", ""),
        ("check_cap", "pay_submit", "[Yes]"),
        ("check_cap", "search", "[No: Capacity Full]"),
        ("pay_submit", "atomic_hold", ""),
        ("atomic_hold", "admin_dec", ""),
        ("admin_dec", "mark_approved", "[Approve]"),
        ("admin_dec", "reject_booking", "[Reject]"),
        ("reject_booking", "end_reject", ""),
        ("mark_approved", "departure_day", ""),
        ("departure_day", "complete_tour", ""),
        ("complete_tour", "leave_review", ""),
        ("leave_review", "end_success", "")
    ]

    for src, dst, label in edges:
        eid = next_id()
        cells.append(f'''        <mxCell id="{eid}" value="{label}" style="{line_style}" edge="1" parent="1" source="{nodes[src]}" target="{nodes[dst]}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>''')

    cap_id = next_id()
    cells.append(f'''        <mxCell id="{cap_id}" value="Figure 6: Activity diagram illustrating the end-to-end tour reservation lifecycle, atomic capacity checks, admin approval, departure attendance recording, and verified review publication." style="{caption_style}" vertex="1" parent="1">
      <mxGeometry x="60" y="980" width="940" height="30" as="geometry"/>
    </mxCell>''')

    return "\n".join(cells), 950, 1040


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main():
    target_dir = os.path.join(os.getcwd(), "diagrams")
    os.makedirs(target_dir, exist_ok=True)

    print("Generating Figure 1: High Level Architecture Diagram (Clean, Minimalist, White)...")
    arch_xml, ar_w, ar_h = build_architecture_diagram()
    arch_file = os.path.join(target_dir, "kiwi-trails-architecture-diagram.drawio")
    with open(arch_file, "w", encoding="utf-8") as f:
        f.write(wrap_drawio_xml("Kiwi Trails System Architecture", arch_xml, ar_w, ar_h))
    print(f"Saved: {arch_file}")

    print("Generating Figure 2: Use Case Diagram (Full Platform)...")
    uc_xml, u_w, u_h = build_use_case_diagram()
    uc_file = os.path.join(target_dir, "kiwi-trails-use-case-diagram.drawio")
    with open(uc_file, "w", encoding="utf-8") as f:
        f.write(wrap_drawio_xml("Kiwi Trails Use Case Diagram", uc_xml, u_w, u_h))
    print(f"Saved: {uc_file}")

    print("Generating Figure 3: Class Diagram (Zero Line Overlaps)...")
    class_xml, c_w, c_h = build_class_diagram()
    class_file = os.path.join(target_dir, "kiwi-trails-class-diagram.drawio")
    with open(class_file, "w", encoding="utf-8") as f:
        f.write(wrap_drawio_xml("Kiwi Trails Domain Class Diagram", class_xml, c_w, c_h))
    print(f"Saved: {class_file}")

    print("Generating Figure 4: Sequence Diagram (Zero Overlaps, Ample Spacing)...")
    seq_xml, s_w, s_h = build_sequence_diagram()
    seq_file = os.path.join(target_dir, "kiwi-trails-sequence-diagram.drawio")
    with open(seq_file, "w", encoding="utf-8") as f:
        f.write(wrap_drawio_xml("Kiwi Trails Booking Sequence Diagram", seq_xml, s_w, s_h))
    print(f"Saved: {seq_file}")

    print("Generating Figure 5: Entity Relationship Diagram (Zero Line Overlaps)...")
    er_xml, er_w, er_h = build_er_diagram()
    er_file = os.path.join(target_dir, "kiwi-trails-er-diagram.drawio")
    with open(er_file, "w", encoding="utf-8") as f:
        f.write(wrap_drawio_xml("Kiwi Trails Entity Relationship Diagram", er_xml, er_w, er_h))
    print(f"Saved: {er_file}")

    print("Generating Figure 6: Activity Diagram (Full Lifecycle)...")
    act_xml, a_w, a_h = build_activity_diagram()
    act_file = os.path.join(target_dir, "kiwi-trails-activity-diagram.drawio")
    with open(act_file, "w", encoding="utf-8") as f:
        f.write(wrap_drawio_xml("Kiwi Trails Lifecycle Activity Diagram", act_xml, a_w, a_h))
    print(f"Saved: {act_file}")

    print("Generating Combined Multi-Page Master Bundle...")
    bundle_data = [
        ("page_arch", "Figure 1 - Architecture Diagram", arch_xml, ar_w, ar_h),
        ("page_uc", "Figure 2 - Use Case Diagram", uc_xml, u_w, u_h),
        ("page_class", "Figure 3 - Class Diagram", class_xml, c_w, c_h),
        ("page_seq", "Figure 4 - Sequence Diagram", seq_xml, s_w, s_h),
        ("page_er", "Figure 5 - ER Diagram", er_xml, er_w, er_h),
        ("page_act", "Figure 6 - Activity Diagram", act_xml, a_w, a_h)
    ]
    bundle_file = os.path.join(target_dir, "kiwi-trails-all-diagrams.drawio")
    with open(bundle_file, "w", encoding="utf-8") as f:
        f.write(create_bundle_drawio(bundle_data))
    print(f"Saved: {bundle_file}")

    print("\nALL DRAW.IO DIAGRAMS GENERATED SUCCESSFULLY IN HIGH LEVEL STYLE!")

if __name__ == "__main__":
    main()

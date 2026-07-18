"use client";

import { useEffect, useMemo, useState } from "react";
import Image from "next/image";

type ChronicleEvent = {
  id: string;
  year: number;
  date: string;
  type: "Battle" | "Court" | "Family" | "Glory" | "Winter";
  title: string;
  description: string;
  people: string[];
  place?: string;
  glory?: number;
};

type ApiItem = { id: string; name: string; description?: string | null; status?: string | null; defensive_value?: number };
type ApiCampaign = {
  current_year: number;
  events: Array<{ id: string; year: number; date?: string | null; event_type: string; title: string; description?: string | null }>;
  families: Array<{ id: string; name: string; origin_location?: string | null; motto?: string | null; culture?: string | null; notes?: string | null; members: ApiItem[] }>;
  manors: Array<{ id: string; name: string; holder?: string | null; customary_income?: string | null; population?: number | null; description?: string | null; improvements: ApiItem[]; special_features: ApiItem[]; defenses: ApiItem[] }>;
  chronicles: Array<{ id: string; year: number; revision: number; title: string; opening: string; closing: string; sections: Array<{ character_id: string; heading: string; body: string }> }>;
};

type AnnualChronicle = ApiCampaign["chronicles"][number];

const demoChronicles: AnnualChronicle[] = [{
  id: "chronicle-485", year: 485, revision: 1,
  title: "The Chronicle of the Year 485",
  opening: "Here is set down the memory of the year 485, that worthy deeds, hard choices, and the turns of fortune should not be lost.",
  closing: "Thus the year was brought to its winter reckoning, and each knight returned to hall and hearth bearing the honor and burden of what had passed.",
  sections: [
    { character_id: "cadry", heading: "Of Sir Cadry", body: "In the rain-swollen Avon valley, Sir Cadry held the crossing while the company recovered the stolen herd. Thereafter a marriage was spoken of between two houses, and the matter was carried onward to the harvest court." },
    { character_id: "elad", heading: "Of Sir Elad", body: "Sir Elad rode with the company against the raiders and returned beneath the recovered banner, his service witnessed by the household of Salisbury." },
  ],
}];

const demoEvents: ChronicleEvent[] = [
  {
    id: "e-1",
    year: 485,
    date: "Early Spring",
    type: "Court",
    title: "The young knights take their oaths",
    description:
      "Before Earl Roderick at Sarum, four household knights swore service to Salisbury and received their first charges.",
    people: ["Sir Elad", "Sir Cadry", "Earl Roderick"],
    place: "Sarum",
  },
  {
    id: "e-2",
    year: 485,
    date: "May",
    type: "Battle",
    title: "Raiders driven from the Avon valley",
    description:
      "A hurried pursuit ended at a rain-swollen ford. Sir Cadry held the crossing while the rest of the company recovered the stolen herd.",
    people: ["Sir Cadry", "Sir Elad"],
    place: "Avon Ford",
    glory: 145,
  },
  {
    id: "e-3",
    year: 485,
    date: "High Summer",
    type: "Family",
    title: "A match proposed between two Salisbury houses",
    description:
      "Lady Elaine welcomed the delegation at Winterbourne. Negotiations will continue after the harvest court.",
    people: ["Lady Elaine", "Sir Cadry"],
    place: "Winterbourne Manor",
  },
  {
    id: "e-4",
    year: 485,
    date: "Winter Phase",
    type: "Winter",
    title: "The household returns to its estates",
    description:
      "Repairs were made, rents collected, and the year’s deeds retold by the hall fire. Cadry’s new squire Oswin began his service.",
    people: ["Sir Cadry", "Oswin"],
    place: "Winterbourne Manor",
  },
  {
    id: "e-5",
    year: 486,
    date: "February",
    type: "Glory",
    title: "The recovered banner is presented at court",
    description:
      "Earl Roderick commended the company before the assembled household and ordered the banner hung in Sarum’s great hall.",
    people: ["Earl Roderick", "Sir Cadry", "Sir Elad"],
    place: "Sarum",
    glory: 75,
  },
];

const people = [
  { initials: "SC", name: "Sir Cadry", role: "Player knight", detail: "Household knight of Salisbury", glory: "1,284" },
  { initials: "SE", name: "Sir Elad", role: "Knight", detail: "Marshal of the household", glory: "3,910" },
  { initials: "OS", name: "Oswin", role: "Squire", detail: "In service to Sir Cadry", glory: "42" },
];

const mapPlaces = [
  { id: "sarum", name: "Sarum", kind: "Castle and court", x: 61.8, y: 72.4, years: "485 onward", note: "Earl Roderick's principal stronghold and the political heart of Salisbury." },
  { id: "salisbury", name: "Salisbury", kind: "Town", x: 62.0, y: 76.4, years: "485 onward", note: "The settlement below Sarum, situated along the Avon." },
  { id: "winterbourne", name: "Winterbourne Earls", kind: "Manor", x: 61.8, y: 68.6, years: "Campaign holding", note: "A manor near the Bourne valley and home to one of the campaign households." },
  { id: "stonehenge", name: "Stonehenge", kind: "Old site", x: 58.8, y: 62.7, years: "Ancient", note: "The great stone circle on Salisbury Plain." },
  { id: "amesbury", name: "Amesbury", kind: "Abbey and town", x: 61.2, y: 63.8, years: "485 onward", note: "A religious house and settlement north of Sarum." },
  { id: "vagon", name: "Vagon", kind: "Manor", x: 47.4, y: 70.4, years: "485 onward", note: "A western Salisbury manor near the Wylye." },
  { id: "warminster", name: "Warminster", kind: "Town", x: 44.3, y: 58.2, years: "485 onward", note: "A market settlement on the western approach to Salisbury Plain." },
  { id: "devizes", name: "Devizes", kind: "Stronghold", x: 51.2, y: 38.4, years: "Period-sensitive", note: "Its lordship and fortification should follow the selected campaign year." },
  { id: "pewsey", name: "Pewsey", kind: "Manor", x: 64.4, y: 42.0, years: "485 onward", note: "A manor in the Vale of Pewsey, north of the plain." },
];

const demoFamilies = [
  { id: "winterbourne", name: "House of Winterbourne", seat: "Winterbourne Earls", motto: "By oath and earth", status: "Landed household", members: 7, heir: "Osric", accent: "W", summary: "A Salisbury knightly family bound to Earl Roderick, with holdings along the Bourne valley." },
  { id: "vagon", name: "House of Vagon", seat: "Vagon Manor", motto: "The wheel endures", status: "Manorial family", members: 5, heir: "Lady Elaine", accent: "V", summary: "An old local lineage whose marriages connect the western manors of the county." },
  { id: "sarum", name: "House of Salisbury", seat: "Sarum", motto: "Steadfast in service", status: "Comital house", members: 9, heir: "Robert", accent: "S", summary: "The ruling household of Salisbury and liege family to the campaign knights." },
];

const familyMembers = [
  { name: "Sir Edar", years: "440–482", relation: "Father", state: "Deceased" },
  { name: "Lady Alys", years: "447–", relation: "Mother", state: "Living" },
  { name: "Sir Cadry", years: "464–", relation: "Household head", state: "Player knight" },
  { name: "Lady Elaine", years: "468–", relation: "Spouse", state: "Living" },
  { name: "Osric", years: "484–", relation: "Son and heir", state: "Living" },
];

const demoManors = [
  { id: "winterbourne-manor", name: "Winterbourne Earls", holder: "Sir Cadry", family: "House of Winterbourne", type: "Knight's fee", income: "£6 annual customary", household: 18, condition: "Sound", place: "winterbourne", note: "A compact estate of arable fields and sheep pasture east of Sarum, held in service to Earl Roderick.", improvements: [{ name: "Timber hall", status: "Complete", year: "Before 480", effect: "Household capacity" }, { name: "Sheep fold", status: "Sound", year: "483", effect: "+ seasonal income" }], features: [{ name: "Clear spring", type: "Natural", detail: "Reliable water through the driest summers" }, { name: "Old boundary stone", type: "Ancient", detail: "Traditional meeting place for the manor court" }], defenses: [{ name: "Ditch and palisade", condition: "Serviceable", strength: "Light defense" }] },
  { id: "vagon-manor", name: "Vagon Manor", holder: "Lady Elaine", family: "House of Vagon", type: "Inherited manor", income: "£7 annual customary", household: 23, condition: "Prosperous", place: "vagon", note: "A western holding near the Wylye with a mill, orchard, and established household.", improvements: [{ name: "Water mill", status: "Complete", year: "478", effect: "+£1 customary income" }, { name: "Apple orchard", status: "Maturing", year: "481", effect: "Autumn produce" }], features: [{ name: "Roman road frontage", type: "Historic", detail: "Fast access to western markets and Sarum" }, { name: "Wylye fishing rights", type: "Right", detail: "Household food and modest rents" }], defenses: [{ name: "Fortified stone undercroft", condition: "Good", strength: "Secure refuge" }] },
  { id: "pewsey-manor", name: "Pewsey Manor", holder: "Sir Elad", family: "Household of Salisbury", type: "Service holding", income: "£5 annual customary", household: 14, condition: "Recovering", place: "pewsey", note: "A Vale of Pewsey estate recovering from poor harvests and recent repairs.", improvements: [{ name: "Drainage channels", status: "In progress", year: "485", effect: "Improved fields" }, { name: "Byre roof", status: "Repair due", year: "485", effect: "Protect livestock" }], features: [{ name: "Chalk pasture", type: "Natural", detail: "Fine grazing on the northern downs" }, { name: "Seasonal fair", type: "Custom", detail: "Three days of local trade after harvest" }], defenses: [{ name: "Earth bank", condition: "Weathered", strength: "Minimal defense" }] },
];

const filters = ["All", "Battle", "Court", "Family", "Glory", "Winter"] as const;

export default function Home() {
  const [events, setEvents] = useState(demoEvents);
  const [families, setFamilies] = useState(demoFamilies);
  const [manors, setManors] = useState(demoManors);
  const [chronicles, setChronicles] = useState(demoChronicles);
  const [year, setYear] = useState(485);
  const [filter, setFilter] = useState<(typeof filters)[number]>("All");
  const [menuOpen, setMenuOpen] = useState(false);
  const [mapYear, setMapYear] = useState<485 | 510>(485);
  const [mapView, setMapView] = useState<"logres" | "salisbury">("logres");
  const [selectedPlace, setSelectedPlace] = useState(mapPlaces[0]);
  const [selectedFamily, setSelectedFamily] = useState(demoFamilies[0]);
  const [selectedManor, setSelectedManor] = useState(demoManors[0]);

  useEffect(() => {
    fetch("/api/campaign")
      .then((response) => {
        if (!response.ok) throw new Error("Campaign data is unavailable");
        return response.json();
      })
      .then((data: ApiCampaign) => {
        const eventTypes: Record<string, ChronicleEvent["type"]> = { battle: "Battle", court: "Court", family: "Family", glory: "Glory", winter: "Winter" };
        const liveEvents = data.events.map((event) => ({
          id: event.id,
          year: event.year,
          date: event.date || "Recorded deed",
          type: eventTypes[event.event_type] || "Court",
          title: event.title,
          description: event.description || "",
          people: [],
        }));
        const liveFamilies = data.families.map((family) => ({
          id: family.id,
          name: family.name,
          seat: family.origin_location || "Seat unrecorded",
          motto: family.motto || "Motto not yet recorded",
          status: family.culture || "Campaign family",
          members: family.members.length,
          heir: "Not yet recorded",
          accent: family.name.charAt(0),
          summary: family.notes || "No public family history has been recorded.",
        }));
        const liveManors = data.manors.map((manor) => ({
          id: manor.id,
          name: manor.name,
          holder: manor.holder || "Holder unrecorded",
          family: "Family affiliation unrecorded",
          type: "Manor",
          income: manor.customary_income ? `£${manor.customary_income} annual customary` : "Income unrecorded",
          household: manor.population || 0,
          condition: "Recorded holding",
          place: manor.name.toLowerCase().replaceAll(" ", "-"),
          note: manor.description || "No public manor description has been recorded.",
          improvements: manor.improvements.map((item) => ({ name: item.name, status: item.status || "Recorded", year: "—", effect: item.description || "" })),
          features: manor.special_features.map((item) => ({ name: item.name, type: "Special", detail: item.description || "" })),
          defenses: manor.defenses.map((item) => ({ name: item.name, condition: "Recorded", strength: `Defensive value ${item.defensive_value}` })),
        }));
        if (liveEvents.length) setEvents(liveEvents);
        if (liveFamilies.length) { setFamilies(liveFamilies); setSelectedFamily(liveFamilies[0]); }
        if (liveManors.length) { setManors(liveManors); setSelectedManor(liveManors[0]); }
        if (data.chronicles?.length) setChronicles(data.chronicles);
        if (data.current_year) setYear(data.current_year);
      })
      .catch(() => undefined);
  }, []);

  const visibleEvents = useMemo(
    () => events.filter((event) => event.year === year && (filter === "All" || event.type === filter)),
    [events, filter, year],
  );
  const annualChronicle = chronicles.find((chronicle) => chronicle.year === year);

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="The Salisbury Chronicle home">
          <span className="brand-mark">P</span>
          <span><strong>The Salisbury Chronicle</strong><small>A Pendragon campaign</small></span>
        </a>
        <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation">Menu</button>
        <nav className={menuOpen ? "nav-open" : ""}>
          <a className="active" href="#chronicle">Chronicle</a>
          <a href="#people">People</a>
          <a href="#places">Places</a>
          <a href="#families">Families</a>
          <button className="search-button" aria-label="Search the chronicle">Search <kbd>/</kbd></button>
        </nav>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">The reign of Uther Pendragon</p>
          <h1>Deeds remembered.<br /><em>Years made legend.</em></h1>
          <p className="lede">The living record of Salisbury’s knights, their households, and the realm they shape—one perilous year at a time.</p>
          <div className="hero-actions">
            <a className="primary-button" href="#chronicle">Read the chronicle <span>↓</span></a>
            <span className="updated"><i /> Last chronicled: Winter 485</span>
          </div>
        </div>
        <aside className="year-card">
          <span className="roman">ANNO DOMINI</span>
          <strong>485</strong>
          <div className="rule"><i /></div>
          <p><b>Current campaign year</b><br />The company has returned to its manors for the Winter Phase.</p>
          <dl>
            <div><dt>4</dt><dd>Knights</dd></div>
            <div><dt>28</dt><dd>Recorded deeds</dd></div>
            <div><dt>3</dt><dd>Great houses</dd></div>
          </dl>
        </aside>
      </section>

      <section className="chronicle-section" id="chronicle">
        <div className="section-heading">
          <div><p className="eyebrow">Recorded history</p><h2>The Chronicle</h2></div>
          <div className="year-switcher" aria-label="Choose campaign year">
            <button onClick={() => setYear(485)} disabled={year === 485} aria-label="Previous year">←</button>
            <span><small>Campaign year</small><b>{year}</b></span>
            <button onClick={() => setYear(486)} disabled={year === 486} aria-label="Next year">→</button>
          </div>
        </div>

        {annualChronicle && (
          <article className="annual-chronicle" aria-labelledby={`annual-chronicle-${annualChronicle.year}`}>
            <header>
              <span>Winter chronicle · revision {annualChronicle.revision}</span>
              <h3 id={`annual-chronicle-${annualChronicle.year}`}>{annualChronicle.title}</h3>
              <p>{annualChronicle.opening}</p>
            </header>
            <div className="annual-chronicle-sections">
              {annualChronicle.sections.map((section) => (
                <section key={section.character_id}>
                  <h4>{section.heading}</h4>
                  <p>{section.body}</p>
                </section>
              ))}
            </div>
            <footer>{annualChronicle.closing}</footer>
          </article>
        )}

        <div className="filter-row" aria-label="Filter chronicle events">
          {filters.map((item) => <button key={item} className={filter === item ? "selected" : ""} onClick={() => setFilter(item)}>{item}</button>)}
        </div>

        <div className="timeline">
          {visibleEvents.map((event) => (
            <article className="event" key={event.id}>
              <div className="event-date"><b>{event.date}</b><span>{event.year}</span></div>
              <div className={`event-icon ${event.type.toLowerCase()}`}>{event.type.charAt(0)}</div>
              <div className="event-copy">
                <span className="event-type">{event.type}</span>
                <h3>{event.title}</h3>
                <p>{event.description}</p>
                <div className="event-meta">
                  <span>{event.people.join(" · ")}</span>
                  {event.place && <span>◇ {event.place}</span>}
                  {event.glory && <strong>+{event.glory} Glory</strong>}
                </div>
              </div>
            </article>
          ))}
          {visibleEvents.length === 0 && <div className="empty-state">No {filter.toLowerCase()} entries have been recorded for {year}.</div>}
        </div>
      </section>

      <section className="people-section" id="people">
        <div className="section-heading">
          <div><p className="eyebrow">Those who shaped the year</p><h2>People of the Chronicle</h2></div>
          <button className="text-button">View all people →</button>
        </div>
        <div className="people-grid">
          {people.map((person) => (
            <article className="person-card" key={person.name}>
              <div className="portrait">{person.initials}</div>
              <span>{person.role}</span><h3>{person.name}</h3><p>{person.detail}</p>
              <div><small>Recorded Glory</small><b>{person.glory}</b></div>
            </article>
          ))}
        </div>
      </section>

      <section className="map-section" id="places">
        <div className="section-heading map-heading">
          <div><p className="eyebrow">Land &amp; lordship</p><h2>{mapView === "logres" ? "Britain & Logres" : "County Salisbury"}</h2></div>
          <div className="era-switcher" aria-label="Choose map period">
            <button className={mapYear === 485 ? "selected" : ""} onClick={() => setMapYear(485)}>Campaign 485</button>
            <button className={mapYear === 510 ? "selected" : ""} onClick={() => setMapYear(510)}>Reference c. 510</button>
          </div>
        </div>
        <div className="map-view-switcher" aria-label="Choose map scale">
          <button className={mapView === "logres" ? "selected" : ""} onClick={() => setMapView("logres")}>Kingdom overview</button>
          <span>→</span>
          <button className={mapView === "salisbury" ? "selected" : ""} onClick={() => setMapView("salisbury")}>Salisbury detail</button>
        </div>
        <p className="map-intro">{mapView === "logres" ? "See Salisbury in the kingdoms and roads of Britain, then descend into the county where the campaign begins." : "Explore the campaign’s manors, courts, roads, and old places. The period overlay controls our campaign annotations; the underlying published cartography is preserved as a circa 510 reference."}</p>
        <div className="map-layout">
          {mapView === "logres" ? (
            <div className={`map-frame kingdom-map era-${mapYear}`}>
              <Image src="/maps/logres-player-map-circa-510.jpg" width={1240} height={1619} priority alt="Player map of Britain and Logres, circa 510" />
              <div className="map-period-label"><b>{mapYear}</b><span>{mapYear === 485 ? "Uther period context" : "Boy King reference"}</span></div>
              <button className="salisbury-focus" onClick={() => setMapView("salisbury")} aria-label="Open detailed map of Salisbury"><i /><span>Salisbury<br /><small>Open county map →</small></span></button>
            </div>
          ) : (
            <div className={`map-frame era-${mapYear}`}>
              <Image src="/maps/salisbury-county-circa-510.jpg" width={2400} height={1545} priority alt="Illustrated map of County Salisbury and the surrounding lands, circa 510" />
              <div className="map-period-label"><b>{mapYear}</b><span>{mapYear === 485 ? "Uther period overlay" : "Boy King reference"}</span></div>
              {mapPlaces.map((place, index) => (
                <button key={place.id} className={`map-marker ${selectedPlace.id === place.id ? "active" : ""}`} style={{ left: `${place.x}%`, top: `${place.y}%` }} onClick={() => setSelectedPlace(place)} aria-label={`View ${place.name}`}><span>{index + 1}</span></button>
              ))}
            </div>
          )}
          <aside className="place-panel">
            <p className="eyebrow">Selected place</p>
            <span className="place-kind">{mapView === "logres" ? "County and homeland" : selectedPlace.kind}</span>
            <h3>{mapView === "logres" ? "Salisbury" : selectedPlace.name}</h3>
            <p>{mapView === "logres" ? "The campaign’s home county lies in southern Logres, west of Silchester and north of the Wessex coast." : selectedPlace.note}</p>
            <dl><dt>Recorded period</dt><dd>{mapView === "logres" ? "Campaign heartland" : selectedPlace.years}</dd><dt>Map view</dt><dd>{mapView === "logres" ? "Kingdom overview" : mapYear === 485 ? "Campaign overlay" : "Original reference era"}</dd></dl>
            <button className="primary-button" onClick={() => setMapView("salisbury")}>{mapView === "logres" ? "Enter County Salisbury" : "County record prototype"} <span>→</span></button>
            {mapYear === 485 && <small className="period-note">Political names and arms printed on the base map may represent the later Boy King era. Campaign markers use the selected year.</small>}
          </aside>
        </div>
        <p className="map-credit">Reference maps supplied by the Gamemaster. Base cartography retained without alteration.</p>
      </section>

      <section className="manors-section" id="manors">
        <div className="section-heading">
          <div><p className="eyebrow">Estates &amp; stewardship</p><h2>Places &amp; Manors</h2></div>
          <a className="text-button" href="#places">Return to maps ↑</a>
        </div>
        <p className="section-intro">Browse the holdings that sustain Salisbury’s households. Each estate record is designed to combine tenure, family, household, improvements, and annual history.</p>
        <div className="record-layout">
          <div className="record-list" role="list" aria-label="Manors">
            {manors.map((manor) => <button role="listitem" key={manor.id} className={selectedManor.id === manor.id ? "selected" : ""} onClick={() => setSelectedManor(manor)}><span className="record-sigil">◇</span><span><small>{manor.type}</small><b>{manor.name}</b><em>{manor.holder}</em></span><i>→</i></button>)}
          </div>
          <article className="manor-record">
            <div className="record-title"><div><p className="eyebrow">Estate record</p><h3>{selectedManor.name}</h3><span>{selectedManor.type} · County Salisbury</span></div><b>{selectedManor.condition}</b></div>
            <p>{selectedManor.note}</p>
            <dl className="stat-grid"><div><dt>Current holder</dt><dd>{selectedManor.holder}</dd></div><div><dt>House</dt><dd>{selectedManor.family}</dd></div><div><dt>Customary income</dt><dd>{selectedManor.income}</dd></div><div><dt>Household</dt><dd>{selectedManor.household} people</dd></div></dl>
            <div className="estate-details">
              <section><div className="estate-detail-heading"><span className="detail-mark improvement-mark">I</span><div><small>Works &amp; investments</small><h4>Improvements</h4></div></div>{selectedManor.improvements.map((item) => <article key={item.name}><div><b>{item.name}</b><span>{item.effect}</span></div><p><em>{item.status}</em><small>{item.year}</small></p></article>)}</section>
              <section><div className="estate-detail-heading"><span className="detail-mark feature-mark">✦</span><div><small>Distinctive qualities</small><h4>Special Features</h4></div></div>{selectedManor.features.map((item) => <article key={item.name}><div><b>{item.name}</b><span>{item.detail}</span></div><p><em>{item.type}</em></p></article>)}</section>
              <section><div className="estate-detail-heading"><span className="detail-mark defense-mark">D</span><div><small>Fortification</small><h4>Defenses</h4></div></div>{selectedManor.defenses.map((item) => <article key={item.name}><div><b>{item.name}</b><span>{item.strength}</span></div><p><em>{item.condition}</em></p></article>)}</section>
            </div>
            <div className="record-timeline"><p className="eyebrow">Recent estate history</p><ol><li><b>485</b><span>Tenure confirmed at Sarum court</span></li><li><b>485</b><span>Winter household and harvest recorded</span></li><li><b>Planned</b><span>Improvement and treasury ledgers</span></li></ol></div>
            <button className="primary-button" onClick={() => { const place = mapPlaces.find((item) => item.id === selectedManor.place); if (place) setSelectedPlace(place); setMapView("salisbury"); document.getElementById("places")?.scrollIntoView(); }}>Show on county map <span>↑</span></button>
          </article>
        </div>
      </section>

      <section className="families-section" id="families">
        <div className="section-heading"><div><p className="eyebrow">Blood &amp; inheritance</p><h2>Families of Salisbury</h2></div><span className="prototype-label">Player-visible lineage</span></div>
        <p className="section-intro">Follow marriages, heirs, household heads, and the relationships that carry the campaign from one generation to the next.</p>
        <div className="family-tabs" role="tablist" aria-label="Families">
          {families.map((family) => <button role="tab" aria-selected={selectedFamily.id === family.id} key={family.id} className={selectedFamily.id === family.id ? "selected" : ""} onClick={() => setSelectedFamily(family)}><span>{family.accent}</span><small>{family.status}</small><b>{family.name}</b><em>{family.seat}</em></button>)}
        </div>
        <div className="family-record">
          <aside className="family-summary"><div className="large-sigil">{selectedFamily.accent}</div><p className="eyebrow">Selected house</p><h3>{selectedFamily.name}</h3><i>“{selectedFamily.motto}”</i><p>{selectedFamily.summary}</p><dl><dt>Family seat</dt><dd>{selectedFamily.seat}</dd><dt>Named members</dt><dd>{selectedFamily.members}</dd><dt>Recognized heir</dt><dd>{selectedFamily.heir}</dd></dl></aside>
          <div className="lineage-panel">
            <div className="lineage-heading"><div><p className="eyebrow">Line of descent</p><h3>Household lineage, 485</h3></div><span>Living &amp; recorded kin</span></div>
            <div className="family-tree">
              <div className="tree-generation parents">{familyMembers.slice(0,2).map((member) => <article key={member.name}><small>{member.relation}</small><b>{member.name}</b><span>{member.years}</span><em>{member.state}</em></article>)}</div>
              <div className="tree-connector"><i /></div>
              <div className="tree-generation couple">{familyMembers.slice(2,4).map((member) => <article key={member.name}><small>{member.relation}</small><b>{member.name}</b><span>{member.years}</span><em>{member.state}</em></article>)}</div>
              <div className="tree-connector"><i /></div>
              <div className="tree-generation heir">{familyMembers.slice(4).map((member) => <article key={member.name}><small>{member.relation}</small><b>{member.name}</b><span>{member.years}</span><em>{member.state}</em></article>)}</div>
            </div>
            <div className="family-events"><p className="eyebrow">Family chronicle</p><span><b>482</b> Sir Edar’s death recorded</span><span><b>483</b> Cadry recognized as household head</span><span><b>484</b> Osric born at Winterbourne</span></div>
          </div>
        </div>
      </section>

      <footer><span className="brand-mark">P</span><p><strong>The Salisbury Chronicle</strong><br />A private campaign record for its players.</p><small>Prototype view · Player-visible records only</small></footer>
    </main>
  );
}

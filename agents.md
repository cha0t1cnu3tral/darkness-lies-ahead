What is the game: Civilization collapsed decades ago. You explore abandoned cities, reclaim buildings, scavenge technology, establish settlements, and encounter competing communities. The game is tern based. It should be fully accessable to the blind, using the nvda screenreader, and audio qs. THe game should be where you navigate tile by tile through places, not jumping between places with arrow key but rather exploring each indevidual tiles with arrows.
Core development elements:
1. 
Use a chunk-based world. Generate and save small sections of the map independently. Don't attempt to generate and simulate the entire world simultaneously.
2\. Separate the game engine from the interface. The engine should independently handle world generation, movement, NPCs, combat, inventory, and interactions. Build a graphical interface for displaying the world and a separate NVDA accessibility layer for reading objects, directions, menus, and game status. Both should use the same game state and mechanics, keeping the game fully graphical and screen-reader accessible without turning it into an audio game.
3. 
Make everything data-driven. Buildings, items, recipes, creatures, and NPC definitions should live in JSON or other structured data. You shouldn't need to modify engine code every time you add a new type of chair.
4. 
Build one universal interaction system. Opening a door, searching a cabinet, talking to an NPC, and using equipment should follow consistent rules.
5. 
Separate world simulation from active simulation. An NPC standing beside you needs detailed behavior. An NPC living in a town 20 kilometers away usually doesn't.
Music and sounds: THe soundtrack to the game should be piano onamus or meloncally music, everything should have an ambiance , everything should be ritch audio wise. Do not cut corners when developing audio systems.

Movement basics:
You are playing as a character in the world. You move your character with arrow keys. You can not walk through walls, you walk into doors or other openables to open them. You walk one tile for each arrow press, if you hold shift plus arrow you run in whatever direction you pointed arrow at. For croutching, you do ctrl+arrow keys. ANd to jump you click space. For movement, there should be different ritch high quality footstep sounds for every type of tile or flooring in the game. 
Combat: First I will give a explaination on how combat should work. Later in this document you will find a list of in world creatures. in After the Collapse is fully turn-based and takes place directly in the open world, without switching to a separate combat screen. Players can move using the arrow keys, run using Shift + Arrow, crouch using Ctrl + Arrow, and jump using Space. Every action consumes a certain amount of in-game time, allowing nearby enemies to respond. Running covers more distance but consumes stamina, while crouching makes the player harder to detect. Players can approach enemies from any direction, retreat, use obstacles for cover, or attempt to escape encounters entirely.
Melee combat uses F for a normal attack, Shift + F for a heavy attack, E to block, and Alt + Arrow to dodge in a specified direction. Pressing Tab cycles through nearby enemies, selecting the target of subsequent attacks. Normal attacks are relatively quick, while heavy attacks consume more stamina and time but deal greater damage. Blocking reduces incoming damage, while dodging moves the character away from an attack. Weapon reach, attack speed, stamina, positioning, and the player's physical condition determine combat effectiveness. Different weapons have distinct properties, and enemies can attack, defend, retreat, or reposition during their turns.
Ranged combat uses A to enter aiming mode, Tab to select targets, F to fire, and R to reload. While aiming, the player can choose between available targets and use additional aiming actions to improve accuracy at the cost of in-game time. Accuracy depends on distance, weapon properties, stance, movement, and environmental conditions. Both melee and ranged combat support tactical positioning, including taking cover behind objects and using terrain to restrict enemy movement. Combat actions provide clear screen-reader feedback describing the action performed, its outcome, and relevant changes to enemy positions or conditions. Players can inspect nearby threats and their own combat status at any time without advancing the turn.
Different things you will find in the world:
1. Residential buildings
Homes, apartments, and places where people lived before the collapse.
1. 
Small suburban house: Wood or brick exterior walls, drywall interior walls, wooden or carpeted floors, asphalt shingle roof. Contains a living room, kitchen, bathroom, one or two bedrooms, closets, and sometimes a garage.
2. 
Medium suburban house: Brick or wood walls, tile and hardwood floors, drywall partitions. Contains multiple bedrooms, bathrooms, a dining room, kitchen, living room, laundry room, and garage.
3. 
Large luxury house: Brick, stone, or concrete walls, marble, tile, and hardwood floors. Contains numerous bedrooms, an office, large kitchen, multiple bathrooms, a basement, and possibly a swimming pool.
4. 
Farmhouse: Wooden walls, timber floors, metal or shingle roof. Contains bedrooms, kitchen, pantry, living areas, and agricultural storage.
5. 
Cabin: Log walls, plank floors, wooden roof, fireplace or stove, beds, storage crates, and basic furniture.
6. 
Mobile home: Thin metal or composite walls, vinyl flooring, lightweight interior partitions, compact bedrooms, kitchen, and bathroom.
7. 
Duplex: Two adjoining residential units with separate entrances, shared structural walls, and individual living areas.
8. 
Townhouse: Narrow multistory residence with brick or wooden walls, staircases, compact rooms, and possibly a small backyard.
9. 
Apartment building: Concrete or brick exterior, drywall partitions, carpet or tile floors, shared hallways, stairwells, and multiple apartments.
10. 
High-rise apartment tower: Reinforced concrete, glass windows, elevators, stairwells, utility rooms, and dozens of apartments.
11. 
Condominium building: Similar to apartments but with varied individual units, balconies, and shared amenities.
12. 
Motel: Concrete or wooden exterior, long walkways, numbered rooms, bathrooms, beds, nightstands, and a reception office.
13. 
Hotel: Concrete, steel, and glass construction, lobby, reception, guest rooms, elevators, restaurant, laundry, and maintenance areas.
14. 
Student dormitory: Brick walls, tiled corridors, shared bedrooms, bathrooms, common rooms, and laundry facilities.
15. 
Retirement home: Concrete or brick walls, accessible corridors, bedrooms, dining areas, medical rooms, and communal spaces.
16. 
Homeless shelter: Shared sleeping rooms, bunk beds, kitchens, bathrooms, supply closets, and administrative offices.
17. 
Residential basement: Concrete walls and floors, exposed pipes, storage shelving, utility equipment, and potentially reinforced shelter rooms.
18. 
Abandoned mansion: Stone or brick exterior, ornate floors, large staircases, extensive rooms, and hidden storage spaces.
19. 
Houseboat: Wooden or metal hull, compact living quarters, deck, and storage compartments.
20. 
Survivalist compound: Reinforced house surrounded by fences, barricades, storage sheds, gardens, and possible underground rooms.
2. Commercial buildings and shops
21. 
Convenience store: Glass storefront, brick walls, tile flooring, checkout counter, refrigerated displays, and shelving.
22. 
Grocery store: Concrete and glass construction, tile floors, food aisles, freezer rooms, stockrooms, and loading docks.
23. 
Supermarket: Large concrete or steel structure with numerous aisles, refrigerated sections, offices, and warehouses.
24. 
Shopping mall: Steel and concrete structure, tiled concourses, numerous shops, food court, elevators, and maintenance corridors.
25. 
Clothing store: Glass storefront, wooden or tile floors, clothing racks, changing rooms, and storage area.
26. 
Shoe store: Shelving, display stands, checkout counter, and stockroom.
27. 
Electronics store: Concrete walls, tile floors, display counters, electronics shelves, and secured storage.
28. 
Hardware store: Concrete flooring, metal shelves, lumber racks, tool displays, and warehouse sections.
29. 
Furniture store: Large showroom containing beds, sofas, chairs, tables, cabinets, and storage rooms.
30. 
Sporting goods store: Display shelves, sporting equipment, camping supplies, storage rooms, and checkout areas.
31. 
Bookstore: Wooden floors, bookshelves, reading tables, storage areas, and office.
32. 
Pharmacy: Tile floors, retail shelves, secured medication storage, and pharmacy counter.
33. 
Medical supply store: Shelves containing medical equipment and supplies, stockrooms, and service counter.
34. 
Pet store: Animal enclosures, shelves, food storage, grooming equipment, and utility rooms.
35. 
Toy store: Shelving, display tables, storage rooms, and checkout counters.
36. 
Jewelry store: Reinforced display counters, glass cases, security shutters, and safe room.
37. 
Pawn shop: Reinforced walls, metal security bars, display counters, shelves, and secured storage.
38. 
Thrift store: Clothing racks, furniture displays, donated goods, shelves, and sorting rooms.
39. 
Department store: Multiple departments, escalators, display areas, storerooms, and offices.
40. 
Garden center: Outdoor plant beds, greenhouses, tool sheds, fertilizer storage, and retail area.
41. 
Auto parts store: Metal shelving, vehicle components, tool displays, and storage room.
42. 
Gas station: Concrete forecourt, fuel pumps, convenience store, storage tanks, bathrooms, and service area.
43. 
Car dealership: Glass showroom, offices, parking lot, vehicle maintenance bays, and inventory yard.
44. 
Laundromat: Tile flooring, washing machines, dryers, folding tables, vending machines, and utility room.
45. 
Barbershop: Chairs, mirrors, counters, sinks, cabinets, and waiting area.
46. 
Beauty salon: Styling stations, wash basins, waiting area, storage closets, and staff room.
47. 
Bank: Concrete walls, service counters, offices, secure vault, and surveillance rooms.
48. 
Post office: Mail counters, sorting rooms, shelves, delivery bays, and employee areas.
49. 
Storage rental facility: Rows of lockable metal units, concrete pathways, fences, and administrative building.
50. 
Public market: Individual stalls, wooden or metal counters, covered walkways, and storage sheds.
3. Restaurants and food establishments
51. 
Fast-food restaurant: Tile floors, kitchen equipment, checkout counters, dining tables, freezers, and bathrooms.
52. 
Diner: Booths, stools, kitchen, food storage, serving counter, and staff areas.
53. 
Family restaurant: Dining rooms, full commercial kitchen, pantry, refrigerated storage, and bathrooms.
54. 
Fine-dining restaurant: Decorative floors, tables, kitchen, storage rooms, and service areas.
55. 
Coffee shop: Counter, espresso equipment, seating areas, pastry displays, and storeroom.
56. 
Bakery: Commercial ovens, preparation tables, ingredient storage, display cases, and sales counter.
57. 
Pizza restaurant: Pizza ovens, kitchen counters, dining space, refrigeration, and storage.
58. 
Bar: Wooden floors, bar counter, bottle shelves, tables, storage, and bathrooms.
59. 
Pub: Bar counter, booths, kitchen, storage cellar, and seating areas.
60. 
Cafeteria: Serving stations, large dining area, kitchens, dishwashing room, and food storage.
61. 
Food truck: Compact metal vehicle body, cooking equipment, counters, and ingredient storage.
62. 
Ice cream shop: Freezers, display cases, tables, counter, and supply room.
63. 
Butcher shop: Refrigerated displays, meat preparation area, freezers, sinks, and storage.
64. 
Food-processing kitchen: Stainless steel counters, industrial cooking equipment, cold storage, and sanitation facilities.
4. Medical buildings
65. 
Hospital: Concrete and steel structure, reception, wards, operating rooms, laboratories, pharmacies, stairwells, elevators, and utility areas.
66. 
Emergency department: Reception, examination rooms, treatment bays, medical storage, and ambulance entrance.
67. 
Urgent care clinic: Waiting area, examination rooms, offices, medical storage, and bathrooms.
68. 
Doctor's office: Reception, consultation rooms, examination rooms, and supply closets.
69. 
Dental clinic: Dental chairs, examination rooms, sterilization rooms, and reception.
70. 
Veterinary clinic: Animal treatment rooms, kennels, surgical rooms, and storage.
71. 
Physical therapy center: Exercise rooms, treatment tables, offices, and equipment closets.
72. 
Mental health clinic: Consultation offices, waiting areas, group rooms, and administrative space.
73. 
Medical laboratory: Laboratory benches, refrigeration, storage cabinets, testing equipment, and ventilation systems.
74. 
Ambulance station: Vehicle garage, equipment storage, staff quarters, and dispatch office.
75. 
Nursing home: Patient rooms, nursing stations, communal areas, kitchens, and utility rooms.
76. 
Medical research facility: Controlled-access laboratories, offices, storage rooms, and specialized equipment.
5. Schools and educational facilities
77. 
Elementary school: Classrooms, hallways, cafeteria, library, offices, playground, and gymnasium.
78. 
Middle school: Classrooms, science labs, gymnasium, cafeteria, library, lockers, and administrative offices.
79. 
High school: Extensive classrooms, laboratories, auditorium, cafeteria, sports facilities, and maintenance rooms.
80. 
University campus: Multiple educational buildings, lecture halls, dormitories, libraries, laboratories, and recreational spaces.
81. 
Community college: Classrooms, workshops, computer labs, offices, and common areas.
82. 
Library: Bookshelves, reading areas, offices, computer stations, and archive rooms.
83. 
Trade school: Mechanical workshops, classrooms, equipment storage, and training facilities.
84. 
Daycare center: Activity rooms, kitchens, bathrooms, offices, and fenced playground.
85. 
Research institute: Laboratories, offices, archives, restricted areas, and technical infrastructure.
86. 
School gymnasium: Wooden sports floor, bleachers, locker rooms, equipment storage, and offices.
87. 
School bus depot: Parking bays, maintenance building, offices, and equipment storage.
6. Government and civic buildings
88. 
Police station: Reception, offices, interview rooms, secure equipment storage, holding cells, and vehicle garage.
89. 
Fire station: Fire-engine bays, equipment lockers, dormitory rooms, kitchen, and offices.
90. 
Town hall: Administrative offices, meeting rooms, archives, reception, and public chambers.
91. 
Courthouse: Courtrooms, offices, holding areas, records storage, and security checkpoints.
92. 
Prison: Reinforced concrete walls, cells, corridors, cafeteria, exercise yards, offices, and perimeter fences.
93. 
Small jail: Holding cells, offices, reception, and secure corridors.
94. 
Emergency operations center: Communications rooms, offices, generators, equipment storage, and reinforced facilities.
95. 
Public works department: Garages, storage yards, maintenance shops, and offices.
96. 
Community center: Meeting rooms, recreation areas, kitchens, bathrooms, and offices.
97. 
Voting center: Large public rooms, desks, storage areas, and administrative offices.
98. 
Municipal archive: Shelving, document rooms, offices, and secured storage.
99. 
Utility administration building: Offices, control rooms, technical equipment, and maintenance areas.
100. 
Public shelter: Reinforced rooms, communal sleeping areas, emergency supply storage, and bathrooms.
7. Industrial buildings
101. 
Factory: Concrete floors, steel beams, machinery, assembly areas, storage, and loading docks.
102. 
Warehouse: Concrete floors, large metal shelving, loading bays, storage crates, and offices.
103. 
Distribution center: Conveyor systems, loading docks, extensive shelving, offices, and vehicle yards.
104. 
Machine shop: Heavy machinery, workbenches, tool storage, and metalworking areas.
105. 
Metal fabrication plant: Industrial equipment, welding stations, raw material storage, and loading zones.
106. 
Lumber mill: Timber processing machinery, lumber stacks, workshops, and storage sheds.
107. 
Sawmill: Cutting equipment, wood storage, conveyors, and maintenance area.
108. 
Textile factory: Production equipment, fabric storage, workshops, and loading bays.
109. 
Food-processing plant: Industrial food equipment, refrigeration, sanitation rooms, and warehouses.
110. 
Chemical plant: Industrial tanks, processing equipment, pipelines, laboratories, and hazardous storage areas.
111. 
Oil refinery: Distillation towers, pipelines, storage tanks, control rooms, and maintenance buildings.
112. 
Water treatment plant: Filtration equipment, settling tanks, pumps, control rooms, and maintenance areas.
113. 
Sewage treatment facility: Treatment tanks, pipes, processing equipment, and utility buildings.
114. 
Power station: Turbines or generators, control rooms, transformers, and equipment storage.
115. 
Electrical substation: Transformers, switchgear, fences, and control equipment.
116. 
Recycling facility: Sorting machinery, waste storage, conveyors, and offices.
117. 
Scrapyard: Open-air piles of metal, vehicle shells, containers, workshops, and fences.
118. 
Quarry: Excavated rock pits, heavy machinery, equipment sheds, and access roads.
119. 
Mine: Underground tunnels, support beams, tracks, ventilation equipment, and extraction machinery.
120. 
Concrete plant: Mixing equipment, material silos, conveyors, and truck loading areas.
121. 
Industrial cold-storage facility: Insulated walls, refrigerated rooms, metal shelves, and mechanical equipment.
122. 
Data center: Server rooms, raised floors, cooling equipment, electrical rooms, and backup generators.
123. 
Telecommunications facility: Equipment racks, cables, transmission equipment, and maintenance offices.
124. 
Construction yard: Heavy machinery, stacked materials, storage containers, and temporary offices.
125. 
Vehicle assembly plant: Production lines, mechanical equipment, storage, and loading docks.
8. Transportation infrastructure
126. 
Residential street: Asphalt road tiles, sidewalks, curbs, driveways, streetlights, and intersections.
127. 
City road: Multiple asphalt lanes, pedestrian crossings, traffic lights, and sidewalks.
128. 
Highway: Wide asphalt lanes, barriers, shoulders, exit ramps, and road signs.
129. 
Dirt road: Packed soil, gravel, ruts, drainage ditches, and vegetation.
130. 
Forest trail: Dirt, roots, stones, shrubs, and occasional fallen trees.
131. 
Parking lot: Asphalt or concrete tiles, marked parking spaces, vehicles, curbs, and lighting.
132. 
Parking garage: Reinforced concrete, ramps, stairwells, elevators, and parking spaces.
133. 
Bus station: Covered platforms, benches, ticket areas, waiting rooms, and vehicle bays.
134. 
Train station: Platforms, tracks, waiting rooms, ticket offices, and maintenance areas.
135. 
Railway tracks: Rails, wooden or concrete sleepers, gravel ballast, switches, and crossings.
136. 
Railway depot: Workshops, storage sheds, train platforms, and maintenance equipment.
137. 
Subway station: Underground platforms, tunnels, stairwells, and technical rooms.
138. 
Subway tunnel: Concrete walls, tracks, maintenance walkways, and service alcoves.
139. 
Airport terminal: Large halls, check-in counters, security areas, gates, offices, and baggage systems.
140. 
Airport runway: Concrete or asphalt pavement, lights, markings, and adjacent taxiways.
141. 
Aircraft hangar: Large steel structure, concrete flooring, aircraft storage, and maintenance equipment.
142. 
Helipad: Reinforced concrete landing pad, markings, lighting, and access paths.
143. 
Marina: Wooden or concrete docks, boat slips, maintenance sheds, and storage areas.
144. 
Shipping port: Concrete loading areas, cranes, warehouses, cargo containers, and docks.
145. 
Bridge: Concrete, steel, or wooden deck, structural supports, barriers, and pedestrian sections.
146. 
Road tunnel: Concrete walls, lighting, ventilation, emergency exits, and maintenance access.
147. 
Truck stop: Fuel stations, parking areas, restaurant, repair shop, and rest facilities.
148. 
Vehicle repair garage: Concrete flooring, hydraulic lifts, tools, spare parts, and workbenches.
149. 
Tire repair shop: Service bays, tire racks, compressors, and storage.
150. 
Bicycle shop: Bicycle racks, tools, repair stands, parts storage, and sales counter.
9. Agricultural locations
151. 
Small family farm: Farmhouse, crop fields, barn, sheds, fences, and dirt tracks.
152. 
Industrial farm: Large agricultural fields, machinery storage, irrigation systems, and silos.
153. 
Barn: Wooden walls, hay storage, animal stalls, loft, and equipment areas.
154. 
Stable: Wooden partitions, feeding troughs, stalls, and tack storage.
155. 
Chicken coop: Wooden enclosure, nesting boxes, perches, and fenced outdoor run.
156. 
Pig enclosure: Fencing, feeding equipment, shelters, and dirt floors.
157. 
Cattle pasture: Grass terrain, fencing, gates, watering troughs, and small shelters.
158. 
Greenhouse: Glass or plastic panels, planting beds, irrigation equipment, and worktables.
159. 
Orchard: Rows of fruit trees, grass, irrigation channels, and service trails.
160. 
Vineyard: Rows of vines, support posts, dirt tracks, and storage sheds.
161. 
Grain silo: Metal or concrete tower, grain storage, ladders, and equipment.
162. 
Agricultural machinery shed: Metal walls, concrete or dirt flooring, tractors, and tools.
163. 
Farm supply warehouse: Fertilizer storage, feed sacks, equipment shelves, and loading areas.
164. 
Irrigation station: Pumps, pipes, control systems, and water channels.
165. 
Fish farm: Water tanks or ponds, pumps, equipment sheds, and walkways.
166. 
Apiary: Beehive boxes, grass terrain, fencing, and equipment shelter.
167. 
Abandoned crop field: Overgrown soil rows, weeds, damaged irrigation, and scattered equipment.
168. 
Community garden: Planting beds, pathways, fencing, compost bins, and shared tools.
169. 
Agricultural research station: Laboratories, greenhouses, test fields, and storage rooms.
170. 
Grain processing mill: Machinery, storage silos, conveyors, and loading facilities.
10. Military and security facilities
171. 
Military checkpoint: Road barriers, guard booth, fencing, observation posts, and vehicle inspection area.
172. 
Military outpost: Barracks, watchtowers, equipment storage, fences, and defensive positions.
173. 
Military base: Barracks, offices, training grounds, garages, warehouses, and secured perimeter.
174. 
Barracks: Shared bedrooms, lockers, bathrooms, common areas, and equipment storage.
175. 
Military warehouse: Reinforced storage areas, metal shelves, crates, and loading docks.
176. 
Vehicle depot: Concrete parking areas, repair bays, vehicle shelters, and storage.
177. 
Training facility: Practice areas, classrooms, obstacle courses, and equipment sheds.
178. 
Radar station: Radar equipment, control building, generators, and security fencing.
179. 
Communications bunker: Underground concrete rooms, electronic equipment, and reinforced doors.
180. 
Emergency command bunker: Reinforced concrete, control rooms, living quarters, storage, and backup utilities.
181. 
Underground military complex: Interconnected tunnels, laboratories, storage areas, secure doors, and technical rooms.
182. 
Abandoned guard tower: Elevated platform, ladder or stairs, supports, and small observation area.
183. 
Security headquarters: Offices, monitoring rooms, equipment lockers, and vehicle bays.
184. 
Armored shelter: Reinforced walls, heavy doors, ventilation equipment, and storage.
185. 
Field encampment: Tents, portable shelters, supply crates, cooking areas, and perimeter barriers.
11. Entertainment and recreation
186. 
Movie theater: Ticket booth, lobby, concession counter, screening rooms, projection room, and bathrooms.
187. 
Bowling alley: Bowling lanes, seating, maintenance machinery, and snack bar.
188. 
Arcade: Game cabinets, service counter, storage area, and bathrooms.
189. 
Gym: Exercise machines, free weights, locker rooms, showers, and offices.
190. 
Indoor swimming pool: Tiled pool basin, walkways, changing rooms, and pump equipment.
191. 
Outdoor swimming pool: Concrete pool, deck, fences, changing rooms, and maintenance shed.
192. 
Stadium: Seating stands, playing field, corridors, concession areas, and service rooms.
193. 
Sports field: Grass or artificial turf, fencing, bleachers, and equipment sheds.
194. 
Basketball court: Concrete or wooden surface, hoops, markings, and seating.
195. 
Tennis court: Hard court or clay surface, fencing, nets, and benches.
196. 
Golf course: Grass fairways, sand bunkers, water hazards, and clubhouse.
197. 
Skate park: Concrete ramps, rails, bowls, and paved paths.
198. 
Public playground: Grass or rubberized ground, slides, swings, climbing structures, and benches.
199. 
Campground: Tent pads, fire rings, picnic tables, toilets, and trails.
200. 
Recreation center: Sports courts, fitness rooms, offices, lockers, and activity rooms.
201. 
Museum: Exhibit rooms, display cases, storage areas, offices, and security rooms.
202. 
Art gallery: Display halls, offices, storage, and workshop rooms.
203. 
Concert hall: Auditorium, stage, backstage rooms, seating, and equipment storage.
204. 
Amusement park: Rides, walkways, food stalls, maintenance buildings, and queue areas.
205. 
Zoo: Animal habitats, fencing, service roads, veterinary buildings, and visitor facilities.
12. Religious, memorial, and community locations
206. 
Small church: Wooden or brick walls, seating, altar, offices, and storage.
207. 
Large cathedral: Stone walls, high ceilings, seating, side rooms, and towers.
208. 
Mosque: Prayer halls, washing facilities, offices, and gathering areas.
209. 
Synagogue: Worship space, seating, offices, classrooms, and storage.
210. 
Temple: Prayer or ceremonial spaces, courtyards, offices, and gardens.
211. 
Cemetery: Grass, soil, pathways, headstones, fences, and small maintenance buildings.
212. 
Mausoleum: Stone walls, interior chambers, corridors, and memorial structures.
213. 
Funeral home: Reception rooms, ceremonial rooms, offices, and service areas.
214. 
Community meeting hall: Seating, stage or podium, kitchens, storage rooms, and bathrooms.
215. 
Public memorial: Stone monuments, engraved plaques, paths, landscaping, and benches.
13. Wilderness and natural locations
216. 
Deciduous forest: Grass, soil, leaf litter, trees, bushes, fallen logs, and rocky terrain.
217. 
Pine forest: Conifer trees, needles, moss, rocks, and dense undergrowth.
218. 
Dense woodland: Closely spaced trees, shrubs, roots, fallen branches, and limited clearings.
219. 
Grassland: Grass tiles, wildflowers, occasional shrubs, and scattered trees.
220. 
Meadow: Tall grass, flowers, bushes, and small water features.
221. 
Swamp: Mud, shallow water, reeds, trees, and unstable ground.
222. 
Marsh: Wet soil, shallow water, grasses, reeds, and small pools.
223. 
River: Flowing water, banks, stones, sand, and bridges or crossings.
224. 
Stream: Shallow flowing water, rocks, dirt banks, and vegetation.
225. 
Lake: Deep and shallow water, shoreline sand, mud, rocks, and docks.
226. 
Pond: Small water body, mud banks, reeds, and aquatic vegetation.
227. 
Waterfall: Elevated water tiles, rock faces, pools, and surrounding vegetation.
228. 
Beach: Sand, gravel, water, driftwood, and coastal vegetation.
229. 
Rocky hillside: Stone tiles, uneven ground, shrubs, and exposed cliffs.
230. 
Mountain: Rock, gravel, snow at suitable elevations, ledges, and caves.
231. 
Cave: Natural stone walls, uneven floors, passages, chambers, and mineral deposits.
232. 
Ravine: Steep dirt or rock walls, narrow pathways, vegetation, and possible water.
233. 
Canyon: Large rock formations, cliffs, trails, and dry riverbeds.
234. 
Desert: Sand, rock, sparse shrubs, and occasional dry riverbeds.
235. 
Wetland: Shallow water, mud, reeds, and vegetation.
236. 
Abandoned quarry lake: Rock walls, flooded excavation areas, and industrial debris.
237. 
Natural spring: Freshwater source, rocks, mud, and surrounding plants.
238. 
Overgrown clearing: Grass, shrubs, fallen trees, and natural debris.
239. 
Burned forest: Charred trees, ash-covered ground, fallen branches, and regenerating vegetation.
240. 
Landslide area: Loose dirt, rocks, broken vegetation, and obstructed pathways.
14. Post-collapse locations
These locations are especially important because they distinguish After the Collapse from an ordinary modern-world simulation.
241. 
Survivor settlement: Improvised houses, gardens, workshops, fences, storage, communal kitchens, and gathering areas.
242. 
Fortified village: Barricades, guard towers, reinforced buildings, gates, and cultivated land.
243. 
Scavenger camp: Tents, makeshift shelters, fires, crates, and piles of salvaged objects.
244. 
Abandoned survivor camp: Collapsed tents, extinguished fire pits, discarded equipment, and scattered possessions.
245. 
Trading post: Market stalls, storage buildings, merchant quarters, and guarded entrances.
246. 
Reclaimed apartment block: Residential units converted into workshops, gardens, kitchens, and communal housing.
247. 
Rooftop settlement: Planters, rainwater collectors, shelters, walkways, and reinforced access points.
248. 
Underground survivor community: Tunnels, sleeping quarters, kitchens, storage chambers, and ventilation infrastructure.
249. 
Refugee shelter: Temporary partitions, sleeping areas, kitchens, sanitation facilities, and supply storage.
250. 
Abandoned evacuation center: Large communal rooms, registration desks, temporary bedding, and supply areas.
251. 
Makeshift hospital: Repurposed building containing beds, medical storage, treatment areas, and sanitation equipment.
252. 
Raider outpost: Barricaded buildings, watchtowers, storage areas, and controlled entrances.
253. 
Bandit roadblock: Vehicles, obstacles, temporary shelters, and observation points.
254. 
Faction headquarters: Reinforced building with offices, meeting rooms, living quarters, and storage.
255. 
Faction-controlled town: Existing urban buildings modified with defenses, checkpoints, workshops, and communal facilities.
256. 
Abandoned battlefield: Damaged vehicles, wrecked structures, debris, and disturbed terrain.
257. 
Collapsed highway encampment: Vehicles converted into shelters, tents, barricades, and cooking areas.
258. 
Improvised workshop: Salvaged machinery, workbenches, tool racks, and stored materials.
259. 
Post-collapse farmstead: Repaired farm buildings, crops, irrigation, livestock enclosures, and defensive fencing.
260. 
Salvage yard: Dismantled equipment, metal piles, workspaces, containers, and organized scrap storage.
261. 
Walled neighborhood: Residential streets enclosed with improvised walls, gates, gardens, and watch posts.
262. 
Remote survival bunker: Reinforced underground rooms, food storage, water tanks, sleeping quarters, and power equipment.
263. 
Abandoned research outpost: Laboratories, temporary housing, communication equipment, and scientific supplies.
264. 
Nomadic caravan camp: Wagons or vehicles, portable shelters, trade supplies, and cooking areas.
265. 
Collapsed skyscraper: Damaged concrete, unstable floors, stairwells, debris, and partially accessible rooms.
266. 
Flooded neighborhood: Submerged streets, waterlogged buildings, floating debris, and elevated walkways.
267. 
Overgrown suburb: Houses surrounded by dense vegetation, broken roads, fallen trees, and abandoned vehicles.
268. 
Quarantined district: Barriers, checkpoints, abandoned medical stations, and sealed buildings.
269. 
Ruined industrial district: Deteriorating factories, warehouses, machinery, debris, and vegetation.
270. 
Reclaimed town center: Restored marketplace, workshops, communal facilities, defenses, and housing.
15. Small structures and world details
These should appear throughout the environment, making exploration more believable.
271. 
Wooden shed: Wooden walls, plank or dirt floor, shelves, tools, and storage.
272. 
Metal storage shed: Sheet-metal walls, concrete or dirt flooring, equipment, and crates.
273. 
Garage: Concrete floor, vehicle space, shelving, tools, and workbench.
274. 
Detached workshop: Wooden or brick walls, workbenches, equipment, and storage.
275. 
Treehouse: Elevated wooden platforms, ladders, railings, and basic shelter.
276. 
Hunting blind: Elevated or ground-level wooden enclosure overlooking wilderness.
277. 
Watchtower: Wooden or metal supports, ladder or stairs, observation platform, and railing.
278. 
Water tower: Elevated metal tank, support structure, ladders, and pipes.
279. 
Radio tower: Metal lattice structure, equipment building, fencing, and service access.
280. 
Wind turbine: Tower, generator housing, foundation, and electrical equipment.
281. 
Solar installation: Solar panels, mounting frames, cables, and equipment shelter.
282. 
Well: Stone or concrete opening, water source, cover, and mechanical pump.
Each of these places should be made up of different tiles, have different objects, and each object with its own propperoities.
Farming: A part of the game is hunting, gathering, and growing food. To farm you should have to have a watering can, soil you can try in the dert of whatever area your in although different dert and places have different propperties and likelyhoods of being excepted or not. ANd fertilizer and similar can help but aren't directly needed, you can also use pestisides if you have them. If you have the watering can, or another thing that holds water it doesn't need to be a watering can. You dig in the dert, using shift plus f to get into farming mode, then arrows to digg in whatever directoin you would like. You can from your enventory if you have a sead, set it in the whole using whatever keyboard shortcut you set as the command for setting stuff down. THis isn't only in farming mode but rather should be the command to set stuff down anywhere in game. THen you move the dert back on, via moving the arrows back where you started. Afterword you water the sead, and as time passes it might or might not grow depending on dert, lighting, and what your using on the plant. Also the invirenment for different plants determanis a lot. 
Hunting: You kill creatures in the game, and can grab the remains with g witch is the in game grab command for anything. When you grab something it puts it in your invetory. Some things you can do with them once you have meet is You then can cook them, see cooking below in the document. You can eat it raw although djepending on the anamal this might make you sick. You can use the skin to make stuff, see crafting later on in the document. You can also use the bones.
Crafting: ## Crafting System

Crafting in After the Collapse should be a detailed, realistic, and flexible survival mechanic that allows players to create tools, weapons, clothing, furniture, shelters, equipment, medicines, and other useful objects from materials found throughout the world. Players can press **C to open the crafting menu**, which displays available recipes organized into categories such as tools, survival equipment, clothing, construction, cooking, medical supplies, and miscellaneous items. Each recipe displays its required materials, tools, skills, crafting time, and available alternatives. Players can search recipes by name or filter them by available resources. Crafting is turn-based, with each action consuming an appropriate amount of in-game time. More complicated projects may require several stages of assembly, specialized workstations, or extended periods of work. Players should also be able to pause unfinished crafting projects and resume them later without losing their progress.

The crafting system should support an extensive range of natural, scavenged, and manufactured materials. Players can gather wood, branches, stones, clay, plant fibers, leaves, vines, leather, animal hides, bones, antlers, teeth, feathers, shells, metal scraps, fabric, plastic, rubber, glass, and mechanical components. Animals should provide different resources depending on their species, including meat, fat, hides, bones, sinew, feathers, and other useful materials. Hides can be processed into leather for crafting clothing, bags, belts, footwear, armor, and furniture coverings. Animal bones and antlers can be shaped into needles, buttons, handles, ornaments, and primitive tools, while sinew can serve as a binding material for certain traditional crafts. Feathers can be used for insulation, bedding, and decorative items. Plant fibers can be processed into cordage, woven into baskets, or used to manufacture simple fabrics. Different materials should possess distinct properties such as weight, durability, flexibility, insulation, and resistance to environmental damage.

Crafting should not be restricted to recipes requiring one exact set of ingredients. Instead, implement a **material substitution system** allowing compatible resources to fulfill the same purpose. For example, a basic shelter might use wooden poles or suitable metal supports, while a storage pouch could be made from leather, heavy fabric, or another flexible material. The resulting item's properties should reflect the materials used. A leather backpack might resist wear differently from a fabric backpack, and a metal tool could have different weight and durability characteristics than a wooden equivalent. Players should also be able to dismantle furniture, salvage abandoned equipment, recycle clothing, and recover usable components from damaged objects. Items should have material compositions so dismantling a wooden chair produces appropriate wooden components and fasteners rather than arbitrary loot.

Crafting should involve tools and workstations that affect what players can produce. Simple items may be crafted directly from the inventory, while more advanced projects require access to workbenches, sewing stations, cooking facilities, woodworking equipment, or mechanical workshops. Tools should have distinct functions, and their quality and condition should influence crafting speed and the quality of finished products. The game should track crafting skills such as woodworking, tailoring, leatherworking, cooking, mechanics, and general fabrication. Beginners should be capable of producing basic objects, while experienced characters can complete more complicated projects more efficiently and with more consistent results. Recipes can be learned through experimentation, books, instructions, NPC training, or practical experience.

Crafting should integrate directly with the open world rather than functioning as an isolated menu. Players should be able to use resources stored in nearby containers, on the ground, or within accessible workstations without manually transferring everything into their inventory. Large projects, such as constructing furniture, repairing vehicles, or building shelters, should take place at their actual world locations. The environment should also affect crafting: rain can interfere with outdoor work, darkness can make precision tasks harder, and certain activities require a suitable workspace. Crafted items should remain persistent, allowing players to repair, customize, upgrade, disassemble, or reuse them as their needs change. The overall goal is to create a **deep, interconnected crafting system where nearly every useful resource in the world has a purpose**, encouraging experimentation, scavenging, hunting, agriculture, and long-term survival planning.
Cooking: ## Cooking and Food Preparation System

Cooking in After the Collapse should be a detailed, interactive survival mechanic that allows players to prepare meals using ingredients gathered, grown, hunted, scavenged, or purchased throughout the world. Players should be able to cook using campfires, fireplaces, wood-burning stoves, gas stoves, electric ovens, grills, portable cooking equipment, and other appropriate heat sources. Cooking should involve selecting ingredients, preparing them, choosing cooking methods, and managing the cooking process. Players can press **C to access cooking recipes through the crafting menu**, or interact directly with a stove, oven, fire, or other cooking station to open its available actions. Recipes should include soups, stews, roasted meats, grilled vegetables, bread, pasta, preserved foods, and complex meals containing multiple ingredients. Every recipe should display the required ingredients, equipment, cooking method, preparation time, and estimated number of servings. Players should also have the freedom to prepare simple meals without following a predefined recipe.

### Fires and Heat Sources

Players should be able to create fires in appropriate locations using fireplaces, existing fire pits, campfire sites, or suitable outdoor ground. A fire requires combustible fuel, such as wood, branches, or other appropriate materials, along with a method of ignition. Rather than treating fire as a simple on/off state, the game should simulate its size, heat output, available fuel, burn duration, and surrounding environmental conditions. Players can interact with a fire to inspect its status, add fuel, adjust the arrangement of cooking equipment, or extinguish it. Larger fires produce more heat and consume fuel more quickly, while smaller fires may be better suited to slow cooking. Rain, wind, and wet materials can make outdoor fires less reliable. Fire should also produce light, smoke, and environmental warmth. Unattended fires may burn out, spread to nearby combustible objects, or create dangerous conditions inside poorly ventilated buildings. Fireplaces and enclosed stoves should behave differently from open campfires, particularly regarding heat retention, fuel consumption, and smoke management.

### Stoves, Ovens, and Cooking Equipment

Kitchen appliances should function as interactive objects rather than decorative furniture. A gas stove requires an available gas supply, an electric stove requires electricity, and a wood-burning stove requires suitable fuel. Players should be able to inspect an appliance to determine whether it works, whether it has sufficient power or fuel, and whether it contains cooking equipment or food. Interacting with a functioning stove should provide actions such as turning burners on or off, choosing a heat setting, placing cookware on a burner, and removing finished food. Ovens should support opening and closing their doors, placing food on racks or trays, adjusting temperature, and starting or stopping heating. In-game oven temperatures and burner settings should influence cooking results, although players should not need to manage every tiny detail of appliance operation. Pots, pans, baking trays, kettles, grills, and other equipment should support different cooking methods. A frying pan can be used for frying and sautéing, while a pot allows boiling, simmering, and preparing soups or stews. Appliances should retain their state between turns, meaning a player who leaves food cooking and walks away may return to find it finished, cold, overcooked, or burned.

### Ingredient Preparation and Cooking Actions

Cooking should consist of multiple meaningful actions rather than instantly transforming raw ingredients into completed dishes. Players should be able to wash ingredients, peel vegetables, chop food, mix ingredients, season meals, combine ingredients in containers, and transfer prepared food into cookware. These interactions should use the same universal object interaction system employed throughout the rest of the game. For example, a player preparing vegetable stew might collect vegetables, meat, water, and seasonings, select an appropriate pot, prepare the ingredients, combine them, and place the pot over a heat source. Each action consumes in-game time, with preparation speed influenced by the player's cooking skill, available tools, and workspace. The system should also support batch preparation, allowing players to prepare multiple servings without unnecessarily repeating every action. Simple recipes should remain convenient, while complex dishes can require more preparation steps and equipment.

### Cooking Progress, Temperature, and Food Quality

Food should cook progressively over time, with its condition determined by the cooking method, temperature, duration, and ingredients. A dish may transition through states such as raw, warming, partially cooked, properly cooked, overcooked, and burned. Some foods are intended to be eaten raw, while others require sufficient cooking to be safe. Different ingredients should have different cooking requirements, meaning vegetables, grains, meat, and baked goods may finish at different rates. Players should be able to inspect cooking food at any time to receive information about its current condition and estimated progress, based on their character's knowledge and cooking skill. Cooking should continue as time advances, including while the player performs unrelated activities nearby. Burning food may reduce its nutritional value, taste, and usefulness. Undercooked or contaminated food may cause illness. Food quality should be influenced by ingredient freshness, cooking skill, seasoning, equipment, and whether the preparation method was appropriate.

### Food Ingredients, Recipes, and Experimentation

The game should contain a large selection of edible ingredients, including vegetables, fruits, grains, beans, mushrooms, herbs, spices, dairy products, eggs, fish, and meat from different animal species. Ingredients should have distinct properties such as nutritional value, freshness, flavor characteristics, water content, and compatibility with different cooking methods. Players should be able to substitute ingredients within reasonable limits, such as using different vegetables in a stew or replacing one suitable type of meat with another. Animal products should integrate with the hunting and farming systems, allowing players to obtain meat, fat, eggs, and milk from appropriate sources. Recipes can be discovered through cookbooks, handwritten notes, NPCs, experimentation, and cooking experience. The game should support both predefined recipes and flexible cooking, where players can combine compatible ingredients to create meals based on general cooking rules. Meals should have recognizable names whenever possible rather than always being labeled as generic mixtures.

### Food Storage, Spoilage, and Preservation

Food should deteriorate realistically over time depending on its type, preparation method, packaging, storage conditions, and surrounding temperature. Raw meat, dairy products, and cooked meals generally spoil more quickly than dry grains, canned foods, or properly preserved ingredients. Refrigerators and freezers should slow spoilage when they have electricity, while cool basements, cellars, and insulated containers may provide more limited preservation. Players should be able to divide meals into portions, store leftovers, transfer food between containers, and reheat suitable dishes. Preservation methods should include drying, smoking, salting, pickling, fermenting, and canning, with appropriate equipment and recipes required. Preserved foods should have different storage lifetimes and nutritional properties. Food should retain information about its ingredients, preparation date, condition, and storage history, allowing spoilage to be calculated consistently even when the player is far away.

### Hunger, Nutrition, and Meal Effects

Food should provide more than a simple reduction in a hunger meter. Characters should have nutritional requirements influenced by their activity, health, and survival conditions. Meals should provide calories, hydration where appropriate, and nutritional characteristics based on their ingredients. A varied diet should support long-term health, while surviving entirely on limited food sources may eventually cause nutritional deficiencies. Eating prepared meals can also influence morale, comfort, and general well-being. Warm meals may be particularly valuable in cold environments, while fresh food and familiar recipes can provide psychological benefits. Different portion sizes should affect fullness and available food supplies. Players should be able to eat directly from suitable containers, share meals with NPCs, or prepare large quantities of food for settlements and expeditions.

### NPC Cooking and Settlement Kitchens

NPCs should use the same basic cooking mechanics as the player. Survivors may prepare meals independently, operate communal kitchens, gather ingredients, and manage food supplies according to their schedules and responsibilities. Settlement kitchens should allow players to assign cooking tasks, select recipes, allocate ingredients, and manage meal production. NPC cooking skill should affect efficiency and meal quality. Cooking equipment should be shared logically, so multiple characters cannot simultaneously use the same occupied cooking space unless the equipment supports it. Players should be able to trade prepared meals, request food from NPCs, and discover recipes associated with different communities. Food shortages, broken appliances, and interruptions to fuel or electricity supplies should meaningfully affect settlement operations.

### Controls, Accessibility, and User Interface

All cooking interactions should be fully accessible through the game's existing graphical interface and NVDA accessibility layer. Players should interact with stoves, ovens, cookware, fires, and ingredients through consistent object interaction menus rather than memorizing dozens of special keyboard shortcuts. The cooking interface should clearly announce the selected equipment, available ingredients, possible recipes, missing requirements, current heat setting, remaining fuel, and cooking progress. Players should be able to inspect food without advancing time, while actions such as preparing ingredients, changing temperature, adding fuel, or removing cookware should consume appropriate turns. Important cooking events, such as a meal finishing or a fire going out, should generate accessible notifications when relevant. **Cooking should feel like a meaningful part of surviving and rebuilding civilization, while avoiding unnecessary micromanagement that makes preparing a basic meal tedious.*

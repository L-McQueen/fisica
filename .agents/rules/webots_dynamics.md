# Webots Track and Dynamic Payload Best Practices

## 1. Decouple Steep Descents from Sharp Curves
- When modeling roller coasters or gravity-driven vehicle tracks, avoid combining steep downhill slopes ($\theta \ge 35^\circ$) with sharp horizontal curves ($R \le 0.25\text{ m}$) simultaneously.
- Combined lateral and vertical g-forces ($a_c > 5g$) induce heavy rolling and yawing moments that cause unanchored vehicles or payloads to tip over or derail.
- **Best Practice**: Implement a straight descent down to the target plane first ($a_c = 0$), followed by a banked horizontal turn flat on the ground plane.

## 2. Mechanical Retention for Dynamic Payloads
- Transport receptacles or open cavities subjected to acceleration variations and centrifugal forces must incorporate positive physical retention.
- **Best Practice**: Include overhanging retention rims or interlocking lips ($5\text{–}10\text{ mm}$ overhang) on top cavity edges to physically block vertical payload bounce or separation.
- Configure contact surfaces with high Coulomb friction ($\mu \ge 0.90$) and high restitution damping (`bounce` $\le 0.02$) to absorb impact kinetic energy.

## 3. C1 Smooth Tangent Transitions
- Avoid abrupt angular creases between connected track segments.
- Use circular or parabolic fillets for crest and valley transitions to guarantee continuous tangent vectors and smooth normal force transitions.

## 4. Superelevation (Banking) Transitions: Avoid Localized Torsional Warp
- When transitioning from a flat straight into a banked curve, **never introduce steep single-sided elevation ramps across short straight sections**.
- A sudden single-sided rise (> 1 cm over < 10 cm) generates an extreme torsional twist (gradient > 15%) that acts as a violent ramp under high-speed wheels (v > 2 m/s), inducing severe roll kick, chassis bottom-out, and wall wedging.
- **Best Practice**:
  - Keep straight approach/settling sections strictly planar and horizontal (dz = 0).
  - Roll in the banking smoothly **along the circular arc itself** over an arc length L >= 15 cm using a C1 smooth curve (e.g. sin^2(u * pi / 2)) with elevation gradient <= 3.5 mm/cm.
  - Guarantee zero geometric discontinuity (0.0 mm position and tangent step) at the exact point of curvature (PC).

## 5. Constrained Vehicle Bounding Objects: Anti-Snagging & Roll Clearance
- **Never place sharp box corners at the outermost perimeter of a vehicle** traveling inside guardrailed tracks or channels.
- When an edge of a rectangular `Box` bounding object hits a curved trimesh face at an incident angle, ODE generates contact impulses that induce violent yaw moments, pivoting the vehicle diagonally and wedging it between channel walls.
- **Best Practice for Track Vehicles**:
  - Place smooth **deflector spheres** (radius 10-15 mm) at the outermost 4 corners of the vehicle perimeter. Any lateral contact with walls slides and ricochets smoothly without yaw spin.
  - Taper or narrow the bottom chassis collider width (e.g., 40-50% narrower than the wheel track) so that during banking rolls of up to 30°, the chassis bottom maintains >= 5 mm clearance above the floor.
  - In high-speed curves (a_c > 1.5 g), flare outer guardrails outward at >= 25°-30° to create an open bobsled bowl (> 115° dihedral angle) that self-centers the vehicle.


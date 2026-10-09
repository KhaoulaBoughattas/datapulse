# DataPulse — Frontend

## JWT storage: localStorage vs. httpOnly cookie
This frontend stores the JWT in localStorage — simple, functional, but
a real XSS tradeoff. Production would proxy through Next.js route
handlers with an httpOnly cookie instead.

## RBAC in the frontend is UX only
`<RoleGate>` hides buttons based on role — the backend's
`require_permission()` is the actual enforcement point regardless of
what renders client-side.

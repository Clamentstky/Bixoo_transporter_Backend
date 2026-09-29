# Frontend to Backend Mapping

## Overview
This document maps the existing React frontend for the BIXOO Transportation module to the required FastAPI backend endpoints. The backend is designed strictly to support the existing UI without introducing unnecessary features or modifying the frontend design.

## Mapping Table

| Frontend Page | Frontend Component | Required API | HTTP Method | Request Data | Response Data | Database Tables | Auth Required | Role |
|---------------|---------------------|--------------|-------------|--------------|---------------|-----------------|---------------|------|
| `/login` | `Login.jsx` | `/api/v1/auth/login` | POST | `email`, `password` | `access_token`, `refresh_token`, `user` | `users` | No | Any |
| | | `/api/v1/auth/refresh` | POST | `refresh_token` | `access_token`, `refresh_token` | `refresh_tokens` | Yes | Any |
| | | `/api/v1/auth/logout` | POST | None | Success message | `refresh_tokens` | Yes | Any |
| `/dashboard` | `Dashboard.jsx` | `/api/v1/transporter/dashboard` | GET | None | `stats`, `recent_loads`, `active_trip` | Multiple tables | Yes | TRANSPORTER |
| `/dashboard` | `Navbar.jsx` / `Dashboard.jsx`| `/api/v1/transporter/availability` | GET / PATCH | `is_online`, `is_available` | Profile status | `transporter_profiles` | Yes | TRANSPORTER |
| `/loads` | `AvailableLoads.jsx` | `/api/v1/transporter/loads` | GET | `search`, `status`, `page`, etc. | Paginated loads | `transport_requests`, `transport_matches` | Yes | TRANSPORTER |
| `/loads/:loadId` | `LoadDetails.jsx` | `/api/v1/transporter/loads/{load_id}` | GET | None | Load details | `transport_requests`, `transport_matches` | Yes | TRANSPORTER |
| `/loads/:loadId` (Accept) | `LoadDetails.jsx` | `/api/v1/transporter/loads/{load_id}/accept` | POST | None | Created `trip` | `transport_matches`, `transport_requests`, `trips` | Yes | TRANSPORTER |
| `/loads/:loadId` (Reject) | `LoadDetails.jsx` | `/api/v1/transporter/loads/{load_id}/reject` | POST | `reason` | Success message | `transport_matches` | Yes | TRANSPORTER |
| `/trips` | `MyTrips.jsx` | `/api/v1/transporter/trips` | GET | `status`, `page` | Paginated trips | `trips` | Yes | TRANSPORTER |
| `/trips/:tripId` | `TripDetails.jsx` / `LiveTrip.jsx` | `/api/v1/transporter/trips/{trip_id}` | GET | None | Trip details, route, load info | `trips`, `trip_locations` | Yes | TRANSPORTER |
| `/trips/:tripId/live` (Location) | `LiveTrip.jsx` | `/api/v1/transporter/trips/{trip_id}/location` | POST | `latitude`, `longitude`, `speed` | Success message | `trip_locations` | Yes | TRANSPORTER |
| `/trips/:tripId/documents` | `TripDocuments.jsx` | `/api/v1/transporter/trips/{trip_id}/documents` | POST / GET / DELETE | `file`, `document_type` | Uploaded document / list | `trip_documents` | Yes | TRANSPORTER |
| `/trips/:tripId` (Status) | `Delivery.jsx` / `TripComplete.jsx` | `/api/v1/transporter/trips/{trip_id}/status` | PATCH | `status` (e.g., DELIVERED) | Updated trip | `trips`, `trip_status_history` | Yes | TRANSPORTER |
| `/wallet` | `Wallet.jsx` | `/api/v1/transporter/wallet` | GET | None | Balances, transactions | `wallet_transactions` | Yes | TRANSPORTER |
| `/wallet` (Settlements) | `Wallet.jsx` | `/api/v1/transporter/settlements` | GET | None | Settlements list | `settlements` | Yes | TRANSPORTER |
| `/profile` | `Profile.jsx` | `/api/v1/transporter/profile` | GET / PATCH | Profile data | Profile data | `users`, `transporter_profiles` | Yes | TRANSPORTER |
| `/profile` (Vehicles) | `Profile.jsx` | `/api/v1/transporter/vehicles` | GET / POST | Vehicle data | Vehicle list / data | `vehicles` | Yes | TRANSPORTER |
| `/notifications` | `Notifications.jsx` | `/api/v1/notifications` | GET | None | Notifications list | `notifications` | Yes | TRANSPORTER |
| `/notifications` | `Notifications.jsx` | `/api/v1/notifications/{id}/read` | PATCH | None | Success message | `notifications` | Yes | TRANSPORTER |

## Status Workflows

### Trip Status Workflow
`ACCEPTED` → `GOING_TO_PICKUP` → `PICKED_UP` → `IN_TRANSIT` → `AT_DELIVERY` → `DELIVERED` → `COMPLETED` → `SETTLED`

### Transport Request Match Status Workflow
`PENDING` → `VIEWED` → `ACCEPTED` / `REJECTED` / `EXPIRED`

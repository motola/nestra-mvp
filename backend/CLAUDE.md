# Alphacon AI — Backend Rules for Claude Code

Architecture rules that must never be broken:

1. All vendor adapters extend BaseVendorAdapter in
   src/integrations/__init__.py
2. All vendor normalisers output AlphaconDevice only
3. Nothing outside integrations/ references vendor
   field names
4. Demo data lives only in src/demo/
5. DEMO_MODE env var controls all demo behaviour
6. Never store or log WiFi passwords
7. Never expose SUPABASE_SERVICE_ROLE_KEY to frontend
8. Never display IP addresses in API responses
   that reach the frontend
9. All database tables created automatically on startup
10. If database unavailable at startup, log and continue

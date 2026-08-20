// Common public email domains
const PUBLIC_MAIL_DOMAINS = new Set([
  "gmail.com",
  "yahoo.com",
  "outlook.com",
  "hotmail.com",
  "icloud.com",
  "mail.com",
  "protonmail.com",
  "tutanota.com",
  "yandex.com",
  "aol.com",
  "gmx.com",
  "zoho.com",
  "fastmail.com",
  "mailbox.org",
  "posteo.de",
  "pm.me",
  "hey.com",
  "temp-mail.org",
  "maildrop.cc",
  "guerrillamail.com",
]);

export function isPublicMailDomain(email: string): boolean {
  const domain = email.split("@")[1]?.toLowerCase();
  return domain ? PUBLIC_MAIL_DOMAINS.has(domain) : false;
}

export function extractOrgNameFromEmail(email: string): string {
  const domain = email.split("@")[1]?.toLowerCase() || "";

  // If public domain, return empty (user should provide org name)
  if (isPublicMailDomain(email)) {
    return "";
  }

  // If custom domain, use the first part (before first dot)
  // e.g., acme.com → acme, company.co.uk → company
  const parts = domain.split(".");
  return parts[0] || "";
}

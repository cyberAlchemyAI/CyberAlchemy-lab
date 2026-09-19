const verifiedProfiles = new WeakSet();

export function markVerifiedDecisionProfile(profile) {
  verifiedProfiles.add(profile);
  return profile;
}

export function isVerifiedDecisionProfile(profile) {
  return profile !== null && typeof profile === "object" && verifiedProfiles.has(profile);
}

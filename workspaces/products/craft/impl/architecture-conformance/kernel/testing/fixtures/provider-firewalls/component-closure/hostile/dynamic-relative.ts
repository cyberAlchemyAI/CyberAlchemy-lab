const relativeSpecifier = "./missing.js";

export const loadDynamicRelative = () => import(relativeSpecifier);

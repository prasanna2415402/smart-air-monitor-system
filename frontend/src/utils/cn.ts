type ClassValue = string | number | null | boolean | undefined | ClassValue[];

function flatten(inputs: ClassValue[], out: string[]) {
  for (const input of inputs) {
    if (!input) continue;
    if (Array.isArray(input)) {
      flatten(input, out);
    } else {
      out.push(String(input));
    }
  }
}

/** Joins conditional class names together, skipping falsy values. */
export function cn(...inputs: ClassValue[]) {
  const out: string[] = [];
  flatten(inputs, out);
  return out.join(" ");
}

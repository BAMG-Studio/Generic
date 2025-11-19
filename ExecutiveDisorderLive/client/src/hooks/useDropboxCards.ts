import { useQuery } from "@tanstack/react-query";
import type { DecisionCard } from "../data/cards";

export function useDropboxCards() {
  return useQuery({
    queryKey: ["dropbox-cards"],
    queryFn: async () => {
      const response = await fetch("/api/dropbox/cards/all");
      if (!response.ok) {
        console.warn("Failed to load cards from Dropbox, using fallback");
        // Return empty array to trigger fallback
        return [];
      }
      const data = await response.json();
      console.log(`✅ Loaded ${data.length} cards from Dropbox`);
      return data as DecisionCard[];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false, // Don't retry on failure
  });
}

export function useDropboxCrisis() {
  return useQuery({
    queryKey: ["dropbox-crisis"],
    queryFn: async () => {
      const response = await fetch("/api/dropbox/json/Replit/ExecutiveDisorder_Assets/Crisis/crisis-events.json");
      if (!response.ok) {
        console.warn("Failed to load crisis from Dropbox");
        return [];
      }
      const data = await response.json();
      return data;
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

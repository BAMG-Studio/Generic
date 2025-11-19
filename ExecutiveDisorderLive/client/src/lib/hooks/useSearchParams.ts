import { useMemo } from "react";
import { useLocation } from "wouter";

export function useSearchParams() {
  const [location] = useLocation();
  
  return useMemo(() => {
    const searchString = location.includes("?") ? location.split("?")[1] : "";
    return new URLSearchParams(searchString);
  }, [location]);
}
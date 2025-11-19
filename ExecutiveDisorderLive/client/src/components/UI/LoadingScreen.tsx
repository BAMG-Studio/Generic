import React from "react";
import { Card } from "../ui/card";

export default function LoadingScreen() {
  return (
    <div className="absolute inset-0 bg-gray-900 flex items-center justify-center">
      <Card className="bg-black/80 text-white p-8 max-w-md w-full mx-4 text-center">
        <h2 className="text-2xl font-bold mb-4">Executive Disorder</h2>
        <div className="mb-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
        </div>
        <p className="text-gray-300">Loading political chaos...</p>
      </Card>
    </div>
  );
}

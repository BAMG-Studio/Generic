import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

// Fallback absurd headlines
const fallbackHeadlines = [
  "BREAKING: President Declares War on Daylight Saving Time, Clock Industry in Chaos",
  "SCANDAL: Senator Caught Using Comic Sans in Official Documents",
  "EXCLUSIVE: Treasury Considers Replacing Currency with Cryptocurrency Called 'FreedomCoin'",
  "URGENT: Congress Votes to Make Pizza a Vegetable Again, Nutritionists Despair",
  "DEVELOPING: White House Lawn Replaced with Astroturf to Save on Gardening Costs",
  "ALERT: National Bird Changed from Eagle to Chicken After Twitter Poll",
  "SHOCK: Supreme Court Rules Emoji Legally Binding in Contracts",
  "CRISIS: Stock Market Crashes After President's Cat Walks Across Keyboard During Trade",
  "REVEALED: Pentagon Admits UFOs Were Just Weather Balloons Filled with Campaign Promises",
  "BREAKING: Congress Unanimously Agrees on Something, Nation Holds Breath",
  "EXCLUSIVE: Vice President Caught Playing Solitaire During Nuclear Summit",
  "UPDATE: National Anthem Remixed with Dubstep, Traditionalists Furious",
  "SCANDAL: Senator's Filibuster Revealed to Be Reading Entire Harry Potter Series",
  "ALERT: Government Shutdown Avoided by Rock-Paper-Scissors Tournament",
  "DEVELOPING: President's Approval Rating Inversely Proportional to Gas Prices, As Always"
];

export default function HeadlineTicker() {
  const [headlines, setHeadlines] = useState<string[]>(fallbackHeadlines);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    // Try to load headlines from cards data
    try {
      const expandedCards = require('../../data/expandedCards').expandedCards;
      if (expandedCards && expandedCards.length > 0) {
        const cardHeadlines = expandedCards
          .filter((card: any) => card.category === 'scandal' || card.category === 'absurd')
          .map((card: any) => `${card.category.toUpperCase()}: ${card.title}`)
          .slice(0, 15);
        
        if (cardHeadlines.length > 0) {
          setHeadlines([...cardHeadlines, ...fallbackHeadlines.slice(0, 5)]);
        }
      }
    } catch (error) {
      console.log('Using fallback headlines');
    }
  }, []);

  const tickerContent = [...headlines, ...headlines].join(' • ');

  return (
    <div 
      className="relative overflow-hidden whitespace-nowrap"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <motion.div
        animate={{ 
          x: isPaused ? 0 : [-2000, 0]
        }}
        transition={{
          x: {
            repeat: Infinity,
            repeatType: "loop",
            duration: 60,
            ease: "linear",
          },
        }}
        className="inline-block"
      >
        <span className="text-white/80 text-sm sm:text-base font-semibold uppercase tracking-wider">
          {tickerContent.split(' • ').map((headline, index) => (
            <span key={index}>
              {index > 0 && (
                <span className="mx-4 text-yellow-400">•</span>
              )}
              <span className="hover:text-yellow-400 transition-colors cursor-pointer">
                {headline}
              </span>
            </span>
          ))}
        </span>
      </motion.div>
    </div>
  );
}
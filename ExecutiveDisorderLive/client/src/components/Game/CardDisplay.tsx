import React from "react";
import { motion } from "framer-motion";
import { useCardImages } from "../../hooks/useCardImages";
import type { DecisionCard } from "../../data/cards";

interface CardDisplayProps {
  card: DecisionCard;
  onSelect: (optionIndex: number) => void;
  disabled?: boolean;
}

export default function CardDisplay({ card, onSelect, disabled = false }: CardDisplayProps) {
  const cardImage = useCardImages(card.id, card.category, card.imageUrl);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -50 }}
      className="w-full max-w-2xl mx-auto"
    >
      {/* Card Container */}
      <div className="bg-black/20 backdrop-blur-xl rounded-2xl overflow-hidden border border-white/10">
        {/* Card Image/Header */}
        <div className="relative h-48 overflow-hidden">
          {cardImage.imageUrl && !cardImage.error ? (
            <img 
              src={cardImage.imageUrl}
              alt={card.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className={`w-full h-full bg-gradient-to-br ${cardImage.gradient} flex items-center justify-center`}>
              <div className="text-6xl animate-pulse">{cardImage.icon}</div>
            </div>
          )}
          
          {/* Overlay gradient for text readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
          
          {/* Category Badge */}
          <div className="absolute top-4 left-4">
            <span className="px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-xs font-semibold text-white uppercase">
              {card.category}
            </span>
          </div>
        </div>
        
        {/* Card Content */}
        <div className="p-6 space-y-4">
          <h2 className="text-2xl font-bold text-white">{card.title}</h2>
          <p className="text-gray-200">{card.description}</p>
          
          {/* Options */}
          <div className="space-y-3 pt-4">
            {card.options.map((option, index) => (
              <motion.button
                key={index}
                whileHover={{ scale: disabled ? 1 : 1.02 }}
                whileTap={{ scale: disabled ? 1 : 0.98 }}
                onClick={() => {
                  console.log('Button clicked!', { index, disabled, cardTitle: card.title });
                  if (!disabled) {
                    onSelect(index);
                  }
                }}
                disabled={disabled}
                className={`
                  w-full p-4 rounded-lg text-left transition-all
                  ${disabled 
                    ? "bg-gray-600/30 cursor-not-allowed opacity-50" 
                    : "bg-white/10 hover:bg-white/20 cursor-pointer backdrop-blur-sm"
                  }
                  border border-white/20
                `}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-white font-medium flex-1">{option.text}</span>
                  {option.actionText && (
                    <span className="px-3 py-1 bg-gradient-to-r from-purple-500/30 to-pink-500/30 rounded-full text-xs font-bold text-white uppercase tracking-wider border border-white/20 backdrop-blur-sm">
                      {option.actionText}
                    </span>
                  )}
                </div>
                
                {/* Show effects preview on hover */}
                <div className="mt-2 flex gap-4 text-xs">
                  {option.effects.popularity !== 0 && (
                    <span className={option.effects.popularity > 0 ? "text-green-400" : "text-red-400"}>
                      Popularity: {option.effects.popularity > 0 ? "+" : ""}{option.effects.popularity}
                    </span>
                  )}
                  {option.effects.stability !== 0 && (
                    <span className={option.effects.stability > 0 ? "text-blue-400" : "text-orange-400"}>
                      Stability: {option.effects.stability > 0 ? "+" : ""}{option.effects.stability}
                    </span>
                  )}
                  {option.effects.media !== 0 && (
                    <span className={option.effects.media > 0 ? "text-purple-400" : "text-pink-400"}>
                      Media: {option.effects.media > 0 ? "+" : ""}{option.effects.media}
                    </span>
                  )}
                  {option.effects.economy !== 0 && (
                    <span className={option.effects.economy > 0 ? "text-yellow-400" : "text-gray-400"}>
                      Economy: {option.effects.economy > 0 ? "+" : ""}{option.effects.economy}
                    </span>
                  )}
                </div>
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
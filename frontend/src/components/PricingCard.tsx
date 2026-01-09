'use client';

import { motion } from 'framer-motion';

interface PricingCardProps {
  tier: string;
  data: {
    name: string;
    monthly_price: number;
    platforms_limit: number;
    description: string;
    features: readonly string[];
  };
  selected: boolean;
  onClick: () => void;
}

export default function PricingCard({ tier, data, selected, onClick }: PricingCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.03, y: -5 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`
        p-6 rounded-xl cursor-pointer transition-all border-2
        ${
          selected
            ? 'bg-purple-500/20 border-purple-500 shadow-lg shadow-purple-500/50 glow'
            : 'bg-slate-900 border-slate-800 hover:border-purple-500/50 glass'
        }
      `}
    >
      <h3 className="text-2xl font-bold text-white mb-2">{data.name}</h3>
      <div className="text-4xl font-black text-purple-500 mb-4">
        ${data.monthly_price}
        <span className="text-sm text-gray-400">/mo</span>
      </div>
      <p className="text-gray-300 text-sm mb-4">{data.description}</p>
      <div className="text-gray-400 text-sm">
        {data.platforms_limit} platforms included
      </div>
      {selected && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-4 text-center text-purple-400 font-semibold"
        >
          ✓ Selected
        </motion.div>
      )}
    </motion.div>
  );
}

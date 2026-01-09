'use client';

import { motion } from 'framer-motion';
import { FaFire } from 'react-icons/fa';
import type { Song } from '@/types';

interface SongCardProps {
  song: Song;
  index: number;
  onViewPost: () => void;
}

export default function SongCard({ song, index, onViewPost }: SongCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`
        glass rounded-2xl p-6 hover:scale-[1.01] transition-all cursor-pointer
        ${song.fire_mode ? 'border-2 border-orange-500/50 glow-pink' : ''}
      `}
    >
      <div className="flex items-start gap-4 mb-4">
        {/* Album Art */}
        <div className="w-20 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-gradient-to-br from-purple-500 to-pink-500">
          {song.art_url ? (
            <img src={song.art_url} alt={song.song} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-white text-2xl">
              🎵
            </div>
          )}
        </div>

        {/* Song Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-xl font-bold text-white truncate">{song.song}</h3>
              <p className="text-gray-400 text-sm truncate">{song.artist_title}</p>
            </div>
            {song.fire_mode && (
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className="flex items-center gap-1 text-orange-400 flex-shrink-0"
              >
                <FaFire className="text-xl" />
                <span className="font-bold text-sm">FIRE</span>
              </motion.div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-white/10">
        <div>
          <div className="text-gray-400 text-xs mb-1">Popularity</div>
          <div className="text-white font-bold text-lg">{song.spotify_popularity}</div>
        </div>
        <div>
          <div className="text-gray-400 text-xs mb-1">Day in Cycle</div>
          <div className="text-white font-bold text-lg">
            {song.days_in_promotion} / 42
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
          <span>Promotion Progress</span>
          <span>{Math.round((song.days_in_promotion / 42) * 100)}%</span>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(song.days_in_promotion / 42) * 100}%` }}
            transition={{ duration: 1, delay: index * 0.1 }}
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
          />
        </div>
      </div>

      {/* View Post Button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={(e) => {
          e.stopPropagation();
          onViewPost();
        }}
        className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors text-sm"
      >
        View Upcoming Post
      </motion.button>
    </motion.div>
  );
}

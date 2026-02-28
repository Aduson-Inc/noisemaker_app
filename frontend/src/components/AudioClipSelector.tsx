'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { songsAPI } from '@/lib/api';

interface AudioClipSelectorProps {
  songId: string;
  audioUrl: string;
  initialClipStart: number | null;
  initialClipEnd: number | null;
  onClipSaved: (clipStart: number, clipEnd: number) => void;
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export default function AudioClipSelector({
  songId,
  audioUrl,
  initialClipStart,
  initialClipEnd,
  onClipSaved,
}: AudioClipSelectorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<any>(null);
  const regionsRef = useRef<any>(null);
  const activeRegionRef = useRef<any>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [clipStart, setClipStart] = useState(initialClipStart ?? 0);
  const [clipEnd, setClipEnd] = useState(initialClipEnd ?? 10);
  const [duration, setDuration] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize WaveSurfer
  useEffect(() => {
    if (!containerRef.current) return;

    let ws: any = null;
    let regions: any = null;
    let destroyed = false;

    const init = async () => {
      const WaveSurfer = (await import('wavesurfer.js')).default;
      const RegionsPlugin = (await import('wavesurfer.js/dist/plugins/regions.esm.js')).default;

      if (destroyed || !containerRef.current) return;

      regions = RegionsPlugin.create();
      regionsRef.current = regions;

      ws = WaveSurfer.create({
        container: containerRef.current,
        waveColor: '#00D4FF',
        progressColor: '#0088AA',
        cursorColor: '#ffffff',
        cursorWidth: 1,
        barWidth: 2,
        barGap: 1,
        barRadius: 1,
        height: 100,
        normalize: true,
        plugins: [regions],
      });
      wsRef.current = ws;

      ws.on('ready', () => {
        if (destroyed) return;
        const dur = ws.getDuration();
        setDuration(dur);
        setIsLoading(false);

        // Create the 10-second region
        const start = initialClipStart ?? 0;
        const end = initialClipEnd ?? Math.min(10, dur);
        const region = regions.addRegion({
          start,
          end,
          color: 'rgba(0, 212, 255, 0.2)',
          drag: true,
          resize: false,
        });
        activeRegionRef.current = region;
        setClipStart(start);
        setClipEnd(end);
      });

      ws.on('play', () => !destroyed && setIsPlaying(true));
      ws.on('pause', () => !destroyed && setIsPlaying(false));
      ws.on('finish', () => !destroyed && setIsPlaying(false));

      // Track region position changes
      regions.on('region-updated', (region: any) => {
        if (destroyed) return;
        setClipStart(region.start);
        setClipEnd(region.end);
        setSaved(false);
      });

      ws.load(audioUrl);
    };

    init();

    return () => {
      destroyed = true;
      if (ws) {
        ws.destroy();
        wsRef.current = null;
        regionsRef.current = null;
        activeRegionRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audioUrl]);

  const handlePlaySelection = useCallback(() => {
    if (!wsRef.current || !activeRegionRef.current) return;
    activeRegionRef.current.play();
  }, []);

  const handlePlayFull = useCallback(() => {
    if (!wsRef.current) return;
    if (isPlaying) {
      wsRef.current.pause();
    } else {
      wsRef.current.play();
    }
  }, [isPlaying]);

  const handleSaveClip = async () => {
    setIsSaving(true);
    setError(null);
    try {
      await songsAPI.saveAudioClip(songId, clipStart, clipEnd);
      setSaved(true);
      onClipSaved(clipStart, clipEnd);
    } catch (err) {
      console.error('Failed to save clip:', err);
      setError('Failed to save clip. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center gap-3">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
            <span className="text-sm text-white/50">Loading waveform...</span>
          </div>
        </div>
      )}

      {/* Waveform Container */}
      <div
        ref={containerRef}
        className={`w-full rounded border border-white/10 bg-white/5 p-2 ${isLoading ? 'h-0 overflow-hidden' : ''}`}
      />

      {/* Controls (hidden while loading) */}
      {!isLoading && (
        <>
          {/* Time Display */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-cyan-400">
              Selected: {formatTime(clipStart)} &mdash; {formatTime(clipEnd)}
            </span>
            <span className="text-xs text-white/30">
              Duration: {formatTime(duration)}
            </span>
          </div>

          {/* Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handlePlaySelection}
              className="border-2 border-cyan-400 bg-transparent px-4 py-2 text-xs font-black uppercase tracking-wider text-cyan-400 transition-all hover:bg-cyan-400/10"
            >
              Play Selection
            </button>

            <button
              onClick={handlePlayFull}
              className="border-2 border-white/20 bg-transparent px-4 py-2 text-xs font-black uppercase tracking-wider text-white/60 transition-all hover:border-white/40 hover:text-white"
            >
              {isPlaying ? 'Pause' : 'Play Full Track'}
            </button>

            <div className="flex-1" />

            <button
              onClick={handleSaveClip}
              disabled={isSaving || saved}
              className={`border-2 px-6 py-2 text-xs font-black uppercase tracking-wider transition-all ${
                saved
                  ? 'border-lime-400 bg-lime-400/10 text-lime-400'
                  : isSaving
                    ? 'cursor-wait border-white/20 text-white/40'
                    : 'border-lime-400 bg-transparent text-lime-400 hover:bg-lime-400/10'
              }`}
            >
              {saved ? (
                <span className="flex items-center gap-2">
                  <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Clip Saved
                </span>
              ) : isSaving ? (
                <span className="flex items-center gap-2">
                  <div className="h-3 w-3 animate-spin rounded-full border border-white/40 border-t-transparent" />
                  Saving...
                </span>
              ) : (
                'Save Clip'
              )}
            </button>
          </div>

          {/* Error */}
          {error && (
            <p className="text-sm text-red-400">{error}</p>
          )}

          {/* Help Text */}
          <p className="text-xs text-white/30">
            Drag the highlighted region to select your 10-second promotional clip.
          </p>
        </>
      )}
    </div>
  );
}

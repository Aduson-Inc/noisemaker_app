'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { dashboardAPI, frankGarageAPI, platformAPI } from '@/lib/api';
import type { SongSlot } from '@/types';

export default function Dashboard() {
  const [userName, setUserName] = useState<string>('Artist');
  const [userId, setUserId] = useState<string | null>(null);

  // Song slots state
  const [songs, setSongs] = useState<SongSlot[]>([]);
  const [slotsUsed, setSlotsUsed] = useState(0);
  const [canAddSong, setCanAddSong] = useState(false);
  const [nextSlotDays, setNextSlotDays] = useState<number | null>(null);
  const [songsLoading, setSongsLoading] = useState(true);

  // Stats state
  const [artTokens, setArtTokens] = useState<number | null>(null);
  const [platformCount, setPlatformCount] = useState<number | null>(null);

  // Get user info from JWT
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          setUserName(payload.name || 'Artist');
          setUserId(payload.user_id || null);
        } catch {
          setUserName('Artist');
        }
      }
    }
  }, []);

  // Load song slots
  useEffect(() => {
    if (!userId) return;
    setSongsLoading(true);
    dashboardAPI.getSongSlots(userId)
      .then((res) => {
        const data = res.data;
        setSongs(data.songs || []);
        setSlotsUsed(data.slots_used || 0);
        setCanAddSong(data.can_add_song || false);
        setNextSlotDays(data.next_slot_opens_in_days ?? null);
      })
      .catch((err) => {
        console.error('Failed to load song slots:', err);
      })
      .finally(() => setSongsLoading(false));
  }, [userId]);

  // Load art tokens
  useEffect(() => {
    if (!userId) return;
    frankGarageAPI.getTokens(userId)
      .then((res) => setArtTokens(res.data.art_tokens ?? 0))
      .catch(() => setArtTokens(0));
  }, [userId]);

  // Load platform count
  useEffect(() => {
    if (!userId) return;
    platformAPI.getConnectionsStatus(userId)
      .then((res) => {
        const selected = res.data.selected_platforms || [];
        setPlatformCount(selected.length);
      })
      .catch(() => setPlatformCount(0));
  }, [userId]);

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'upcoming': return 'text-cyan-400 border-cyan-400';
      case 'building': return 'text-cyan-400 border-cyan-400';
      case 'live': return 'text-lime-400 border-lime-400';
      case 'twilight': return 'text-amber-400 border-amber-400';
      case 'retired': return 'text-white/40 border-white/40';
      default: return 'text-cyan-400 border-cyan-400';
    }
  };

  const getStageLabel = (song: SongSlot) => {
    if (song.promotion_status === 'pending') {
      return song.go_live_date ? `Goes live ${song.go_live_date}` : 'Pending';
    }
    if (song.promotion_status === 'draft') return 'Draft';
    return song.stage_of_promotion.charAt(0).toUpperCase() + song.stage_of_promotion.slice(1);
  };

  const getProgressPercent = (days: number) => {
    return Math.min(100, Math.round((days / 42) * 100));
  };

  return (
    <main className="relative min-h-screen w-full overflow-x-hidden bg-black">
      {/* Noise texture */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative z-10">
        {/* Header */}
        <header className="flex items-center justify-between border-b-4 border-white px-4 py-4 md:px-8">
          <Link href="/dashboard" className="flex items-center gap-2">
            <Image
              src="/n-logo.png"
              alt="NOiSEMaKER"
              width={40}
              height={40}
              className="h-8 w-8 md:h-10 md:w-10"
            />
            <span className="text-lg font-black uppercase tracking-tight text-white">
              NOiSEMaKER
            </span>
          </Link>

          <button
            onClick={() => {
              localStorage.removeItem('auth_token');
              localStorage.removeItem('user_tier');
              document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
              window.location.href = '/';
            }}
            className="border-2 border-white bg-transparent px-4 py-2 text-sm font-black uppercase tracking-widest text-white transition-all hover:bg-white hover:text-black"
          >
            Sign Out
          </button>
        </header>

        {/* Welcome Banner */}
        <section className="border-b-4 border-fuchsia-500 bg-fuchsia-500 px-4 py-8 md:px-8 md:py-12">
          <div className="mx-auto max-w-7xl">
            <p className="text-sm font-bold uppercase tracking-widest text-black/70">
              Welcome back,
            </p>
            <h1 className="text-4xl font-black uppercase leading-none tracking-tighter text-black md:text-6xl lg:text-7xl">
              {userName}
            </h1>
          </div>
        </section>

        {/* Songs Section */}
        <section className="px-4 py-8 md:px-8 md:py-12">
          <div className="mx-auto max-w-7xl">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-sm font-black uppercase tracking-widest text-white/50">
                Your Songs
              </h2>
              <span className="text-xs font-bold uppercase text-white/30">
                {slotsUsed} / 3 slots
              </span>
            </div>

            {songsLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse border-4 border-white/10 bg-white/5 p-6">
                    <div className="h-40 bg-white/10" />
                    <div className="mt-4 h-4 w-3/4 bg-white/10" />
                    <div className="mt-2 h-3 w-1/2 bg-white/10" />
                  </div>
                ))}
              </div>
            ) : songs.length === 0 ? (
              <div className="border-4 border-dashed border-white/20 p-12 text-center">
                <p className="text-lg font-black uppercase text-white/40">
                  No songs yet
                </p>
                <p className="mt-2 text-sm text-white/30">
                  Complete onboarding to add your first songs
                </p>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {/* Song Cards */}
                {songs.map((song) => (
                  <div
                    key={song.song_id}
                    className="group border-4 border-white/20 bg-black transition-all hover:border-white/40"
                  >
                    {/* Album Art */}
                    <div className="relative aspect-square w-full overflow-hidden bg-white/5">
                      {song.album_art_url ? (
                        <img
                          src={song.album_art_url}
                          alt={song.title}
                          className="h-full w-full object-cover"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center">
                          <span className="text-4xl font-black text-white/10">
                            {song.title.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      )}

                      {/* Fire Mode Indicator */}
                      {song.fire_mode && (
                        <div className="absolute right-2 top-2 flex items-center gap-1 bg-black/80 px-2 py-1">
                          <span className="text-lg">&#128293;</span>
                          <span className="text-xs font-black uppercase text-orange-400">
                            Fire Mode
                          </span>
                        </div>
                      )}

                      {/* Status Badge */}
                      <div className={`absolute left-2 top-2 border-2 bg-black/80 px-2 py-1 text-xs font-black uppercase ${getStageColor(song.stage_of_promotion)}`}>
                        {getStageLabel(song)}
                      </div>
                    </div>

                    {/* Song Info */}
                    <div className="p-4">
                      <h3 className="truncate text-lg font-black uppercase text-white">
                        {song.title}
                      </h3>
                      <p className="truncate text-sm text-white/50">
                        {song.artist}
                      </p>

                      {/* Progress Bar */}
                      {song.promotion_status === 'active' && (
                        <div className="mt-3">
                          <div className="mb-1 flex items-center justify-between">
                            <span className="text-xs font-bold text-white/50">
                              Day {song.days_in_promotion} of 42
                            </span>
                            <span className="text-xs font-bold text-cyan-400">
                              {getProgressPercent(song.days_in_promotion)}%
                            </span>
                          </div>
                          <div className="h-2 w-full bg-white/10">
                            <div
                              className="h-full bg-cyan-400 transition-all"
                              style={{ width: `${getProgressPercent(song.days_in_promotion)}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {/* Audio Clip Indicator */}
                      <div className="mt-3 flex items-center gap-2">
                        {song.has_clip ? (
                          <span className="flex items-center gap-1 text-xs font-bold text-lime-400">
                            <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            Audio Clip Ready
                          </span>
                        ) : song.has_audio ? (
                          <span className="text-xs font-bold text-amber-400">
                            Audio uploaded — needs clip
                          </span>
                        ) : (
                          <span className="text-xs font-bold text-white/30">
                            No audio clip
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Add New Song Card */}
                {canAddSong && (
                  <Link
                    href="/dashboard/add-song"
                    className="group flex flex-col items-center justify-center border-4 border-dashed border-fuchsia-500/40 bg-black p-12 transition-all hover:border-fuchsia-500 hover:bg-fuchsia-500/5"
                  >
                    <div className="flex h-16 w-16 items-center justify-center border-4 border-fuchsia-500/40 text-3xl font-black text-fuchsia-500/40 transition-all group-hover:border-fuchsia-500 group-hover:text-fuchsia-500">
                      +
                    </div>
                    <span className="mt-4 text-sm font-black uppercase tracking-widest text-fuchsia-500/60 transition-all group-hover:text-fuchsia-500">
                      Add New Song
                    </span>
                  </Link>
                )}
              </div>
            )}

            {/* Planning Text */}
            {!songsLoading && slotsUsed > 0 && slotsUsed < 3 && (
              <div className="mt-6 border-2 border-white/10 bg-white/5 p-4">
                {nextSlotDays !== null && !canAddSong ? (
                  <p className="text-sm text-white/50">
                    <span className="font-bold text-white/70">Next slot opens in {nextSlotDays} days.</span>{' '}
                    Plan ahead! Upload your next song to your distributor (DistroKid, TuneCore, etc.)
                    at least 1 month before release. Tell us the go-live date and we&apos;ll start
                    building buzz 14 days early.
                  </p>
                ) : (
                  <p className="text-sm text-white/50">
                    Plan ahead! Upload your next song to your distributor (DistroKid, TuneCore, etc.)
                    at least 1 month before release. Tell us the go-live date and we&apos;ll start
                    building buzz 14 days early.
                  </p>
                )}
              </div>
            )}
          </div>
        </section>

        {/* Tools Section */}
        <section className="border-t-4 border-white/10 px-4 py-8 md:px-8 md:py-12">
          <div className="mx-auto max-w-7xl">
            <h2 className="mb-6 text-sm font-black uppercase tracking-widest text-white/50">
              Your Tools
            </h2>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Frank's Garage Card */}
              <Link
                href="/dashboard/garage"
                className="group border-4 border-fuchsia-500 bg-black p-6 transition-all hover:bg-fuchsia-500/10"
              >
                <div className="text-5xl font-black text-fuchsia-500">01</div>
                <h3 className="mt-2 text-2xl font-black uppercase text-white">
                  Frank&apos;s Garage
                </h3>
                <p className="mt-2 text-sm text-white/50">
                  AI-generated album art marketplace. Download free with tokens or purchase exclusive artwork.
                </p>
                <div className="mt-4 flex items-center gap-2 text-sm font-bold text-fuchsia-500">
                  Browse Art
                  <span className="transition-transform group-hover:translate-x-2">&#8594;</span>
                </div>
              </Link>

              {/* Analytics Card (Coming Soon) */}
              <div className="border-4 border-white/20 bg-black p-6 opacity-50">
                <div className="text-5xl font-black text-white/30">02</div>
                <h3 className="mt-2 text-2xl font-black uppercase text-white/50">
                  Analytics
                </h3>
                <p className="mt-2 text-sm text-white/30">
                  Track engagement, reach, and growth across all your connected platforms.
                </p>
                <div className="mt-4 text-sm font-bold text-white/30">
                  Coming Soon
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Stats */}
        <section className="border-t-4 border-white/20 bg-black px-4 py-8 md:px-8">
          <div className="mx-auto max-w-7xl">
            <h2 className="mb-6 text-sm font-black uppercase tracking-widest text-white/50">
              Quick Stats
            </h2>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="border-2 border-lime-400/30 p-4">
                <div className="text-3xl font-black text-lime-400">
                  {artTokens !== null ? artTokens : '--'}
                </div>
                <div className="text-xs font-bold uppercase text-white/50">Art Tokens</div>
              </div>
              <div className="border-2 border-cyan-400/30 p-4">
                <div className="text-3xl font-black text-cyan-400">{slotsUsed}</div>
                <div className="text-xs font-bold uppercase text-white/50">Songs Active</div>
              </div>
              <div className="border-2 border-fuchsia-500/30 p-4">
                <div className="text-3xl font-black text-fuchsia-500">
                  {songs.filter(s => s.fire_mode).length > 0
                    ? songs.filter(s => s.fire_mode).length
                    : '--'}
                </div>
                <div className="text-xs font-bold uppercase text-white/50">
                  {songs.filter(s => s.fire_mode).length > 0 ? 'In Fire Mode' : 'Fire Mode'}
                </div>
              </div>
              <div className="border-2 border-white/30 p-4">
                <div className="text-3xl font-black text-white">
                  {platformCount !== null ? platformCount : '--'}
                </div>
                <div className="text-xs font-bold uppercase text-white/50">Platforms</div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t-4 border-white bg-black px-4 py-6 text-center md:px-8">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-600">
            NOiSEMaKER by DooWopp &copy; 2026
          </p>
        </footer>
      </div>
    </main>
  );
}

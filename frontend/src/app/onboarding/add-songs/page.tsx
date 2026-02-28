'use client';

import { useEffect, useState, useCallback, lazy, Suspense } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { songsAPI, platformAPI } from '@/lib/api';

const AudioClipSelector = lazy(() => import('@/components/AudioClipSelector'));

/**
 * ADD SONGS - Final Onboarding Step (Step 4 of 4)
 *
 * Gen Z Bold editorial design with:
 * - Staggered entrance animations
 * - Vinyl record-inspired song cards
 * - Glitch effects on validation
 * - High contrast brutalist typography
 */

interface SongForm {
  id: number;
  label: string;
  sublabel: string;
  initialDays: number;
  requiresReleaseDate: boolean;
}

interface ValidatedSong {
  track_id: string;
  name: string;
  artist_name: string;
  album_art_url?: string;
  preview_url?: string;
  popularity?: number;
  release_date?: string;
}

interface SongState {
  url: string;
  releaseDate: string;
  isValidating: boolean;
  isValid: boolean;
  error: string | null;
  validatedData: ValidatedSong | null;
  // Audio upload state
  dbSongId: string | null;
  audioUploading: boolean;
  audioUploadProgress: number;
  audioUploaded: boolean;
  audioUrl: string | null;
  clipStart: number | null;
  clipEnd: number | null;
  clipSaved: boolean;
  audioSkipped: boolean;
}

const SONG_FORMS: SongForm[] = [
  {
    id: 1,
    label: 'UPCOMING RELEASE',
    sublabel: 'A track dropping in 2+ weeks',
    initialDays: 0,
    requiresReleaseDate: true,
  },
  {
    id: 2,
    label: 'YOUR BEST TRACK',
    sublabel: 'Most popular release ever',
    initialDays: 14,
    requiresReleaseDate: false,
  },
  {
    id: 3,
    label: 'SECOND HOTTEST',
    sublabel: 'Your runner-up banger',
    initialDays: 28,
    requiresReleaseDate: false,
  },
];

const TIER_COLORS = {
  talent: {
    bg: 'bg-cyan-400',
    text: 'text-cyan-400',
    border: 'border-cyan-400',
    glow: 'shadow-[0_0_30px_rgba(34,211,238,0.3)]',
    gradient: 'from-cyan-400/20 via-transparent to-transparent',
    hex: '#22d3ee',
  },
  star: {
    bg: 'bg-fuchsia-500',
    text: 'text-fuchsia-500',
    border: 'border-fuchsia-500',
    glow: 'shadow-[0_0_30px_rgba(217,70,239,0.3)]',
    gradient: 'from-fuchsia-500/20 via-transparent to-transparent',
    hex: '#d946ef',
  },
  legend: {
    bg: 'bg-lime-400',
    text: 'text-lime-400',
    border: 'border-lime-400',
    glow: 'shadow-[0_0_30px_rgba(163,230,54,0.3)]',
    gradient: 'from-lime-400/20 via-transparent to-transparent',
    hex: '#a3e635',
  },
};

export default function AddSongsPage() {
  const router = useRouter();

  const [tier, setTier] = useState<'talent' | 'star' | 'legend'>('talent');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  const emptySongState: SongState = {
    url: '', releaseDate: '', isValidating: false, isValid: false, error: null, validatedData: null,
    dbSongId: null, audioUploading: false, audioUploadProgress: 0, audioUploaded: false,
    audioUrl: null, clipStart: null, clipEnd: null, clipSaved: false, audioSkipped: false,
  };

  const [songs, setSongs] = useState<Record<number, SongState>>({
    1: { ...emptySongState },
    2: { ...emptySongState },
    3: { ...emptySongState },
  });

  const getUserId = (): string | null => {
    if (typeof window === 'undefined') return null;
    const token = localStorage.getItem('auth_token');
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.sub || payload.user_id || null;
    } catch {
      return null;
    }
  };

  useEffect(() => {
    setMounted(true);
    const fetchTier = async () => {
      const userId = getUserId();
      if (!userId) {
        setError('Please sign in to continue');
        setIsLoading(false);
        return;
      }

      try {
        const response = await platformAPI.getConnectionsStatus(userId);
        const fetchedTier = response.data.subscription_tier;
        if (fetchedTier && fetchedTier !== 'pending') {
          setTier(fetchedTier);
        }
      } catch (err) {
        console.error('Error fetching user tier:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTier();
  }, []);

  const validateUrl = useCallback(async (songId: number, url: string) => {
    if (!url.trim()) {
      setSongs((prev) => ({
        ...prev,
        [songId]: { ...prev[songId], isValidating: false, isValid: false, error: null, validatedData: null },
      }));
      return;
    }

    if (!url.includes('spotify.com/track/') && !url.includes('spotify:track:')) {
      setSongs((prev) => ({
        ...prev,
        [songId]: { ...prev[songId], isValidating: false, isValid: false, error: 'Invalid Spotify URL', validatedData: null },
      }));
      return;
    }

    setSongs((prev) => ({ ...prev, [songId]: { ...prev[songId], isValidating: true, error: null } }));

    try {
      const response = await songsAPI.validateTrack(url);
      const data = response.data;

      if (data.valid) {
        // Immediately create song as draft so we have a song_id for audio upload
        const form = SONG_FORMS.find((f) => f.id === songId);
        let dbSongId: string | null = null;
        try {
          const addRes = await songsAPI.addSongFromUrl(
            url,
            form?.initialDays ?? 0,
            undefined // release_date added later via apply_stagger
          );
          dbSongId = addRes.data?.song_id || addRes.data?.song?.song_id || null;
        } catch (addErr) {
          console.error('Failed to create draft song:', addErr);
        }

        setSongs((prev) => ({
          ...prev,
          [songId]: {
            ...prev[songId],
            isValidating: false,
            isValid: true,
            error: null,
            dbSongId,
            validatedData: {
              track_id: data.track_id!,
              name: data.name!,
              artist_name: data.artist_name!,
              album_art_url: data.album_art_url,
              preview_url: data.preview_url,
              popularity: data.popularity,
              release_date: data.release_date,
            },
          },
        }));
      } else {
        setSongs((prev) => ({
          ...prev,
          [songId]: { ...prev[songId], isValidating: false, isValid: false, error: data.error || 'Invalid track', validatedData: null },
        }));
      }
    } catch {
      setSongs((prev) => ({
        ...prev,
        [songId]: { ...prev[songId], isValidating: false, isValid: false, error: 'Validation failed', validatedData: null },
      }));
    }
  }, []);

  useEffect(() => {
    const timers: Record<number, NodeJS.Timeout> = {};
    Object.entries(songs).forEach(([id, song]) => {
      if (song.url && !song.isValid && !song.isValidating) {
        timers[Number(id)] = setTimeout(() => validateUrl(Number(id), song.url), 600);
      }
    });
    return () => Object.values(timers).forEach(clearTimeout);
  }, [songs, validateUrl]);

  const handleUrlChange = (songId: number, url: string) => {
    setSongs((prev) => ({
      ...prev,
      [songId]: { ...prev[songId], url, isValid: false, validatedData: null, error: null },
    }));
  };

  const handleReleaseDateChange = (songId: number, date: string) => {
    setSongs((prev) => ({ ...prev, [songId]: { ...prev[songId], releaseDate: date } }));
  };

  const handleClearSong = (songId: number) => {
    setSongs((prev) => ({
      ...prev,
      [songId]: { ...emptySongState },
    }));
  };

  const handleAudioUpload = async (songId: number, file: File) => {
    const songState = songs[songId];
    if (!songState.dbSongId) {
      setSongs((prev) => ({ ...prev, [songId]: { ...prev[songId], error: 'Song not saved yet' } }));
      return;
    }

    const contentType = file.type === 'audio/wav' ? 'audio/wav' : 'audio/mpeg';

    setSongs((prev) => ({
      ...prev,
      [songId]: { ...prev[songId], audioUploading: true, audioUploadProgress: 0, error: null },
    }));

    try {
      // Step 1: Get presigned upload URL
      const urlRes = await songsAPI.getAudioUploadUrl(songState.dbSongId, contentType);
      const { upload_url } = urlRes.data;

      // Step 2: Upload to S3 via XHR for progress tracking
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            const pct = Math.round((e.loaded / e.total) * 100);
            setSongs((prev) => ({
              ...prev,
              [songId]: { ...prev[songId], audioUploadProgress: pct },
            }));
          }
        };
        xhr.onload = () => (xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`Upload failed: ${xhr.status}`)));
        xhr.onerror = () => reject(new Error('Upload failed'));
        xhr.open('PUT', upload_url);
        xhr.setRequestHeader('Content-Type', contentType);
        xhr.send(file);
      });

      // Step 3: Confirm upload (triggers WAV→MP3 conversion if needed)
      await songsAPI.confirmAudioUpload(songState.dbSongId);

      // Step 4: Get presigned audio URL for playback
      const audioRes = await songsAPI.getAudioUrl(songState.dbSongId);
      const audioData = audioRes.data;

      setSongs((prev) => ({
        ...prev,
        [songId]: {
          ...prev[songId],
          audioUploading: false,
          audioUploadProgress: 100,
          audioUploaded: true,
          audioUrl: audioData.audio_url,
          clipStart: audioData.clip_start,
          clipEnd: audioData.clip_end,
        },
      }));
    } catch (err) {
      console.error('Audio upload failed:', err);
      setSongs((prev) => ({
        ...prev,
        [songId]: { ...prev[songId], audioUploading: false, audioUploadProgress: 0, error: 'Audio upload failed' },
      }));
    }
  };

  const handleSkipAudio = (songId: number) => {
    setSongs((prev) => ({
      ...prev,
      [songId]: { ...prev[songId], audioSkipped: true },
    }));
  };

  const handleClipSaved = (songId: number, clipStart: number, clipEnd: number) => {
    setSongs((prev) => ({
      ...prev,
      [songId]: { ...prev[songId], clipStart, clipEnd, clipSaved: true },
    }));
  };

  const getMinReleaseDate = (): string => {
    const date = new Date();
    date.setDate(date.getDate() + 14);
    return date.toISOString().split('T')[0];
  };

  const validSongCount = Object.values(songs).filter((s) => s.isValid).length;
  const canContinue = validSongCount >= 1;
  const song1NeedsReleaseDate = songs[1].isValid && !songs[1].releaseDate;

  const handleContinue = async () => {
    const userId = getUserId();
    if (!userId) { setError('Please sign in'); return; }
    if (song1NeedsReleaseDate) { setError('Enter release date for Song 1'); return; }

    setIsSubmitting(true);
    setError(null);

    try {
      // Songs are already created as drafts during validation.
      // Apply stagger to transition draft → active with correct days.
      await songsAPI.applyStagger();
      router.push('/dashboard');
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to complete onboarding');
      setIsSubmitting(false);
    }
  };

  const tierColors = TIER_COLORS[tier];

  return (
    <main className="relative min-h-screen w-full overflow-x-hidden bg-black">
      {/* CSS Animations */}
      <style jsx global>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(40px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 20px ${tierColors.hex}40; }
          50% { box-shadow: 0 0 40px ${tierColors.hex}60; }
        }
        @keyframes spin-vinyl {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes glitch {
          0%, 100% { transform: translate(0); }
          20% { transform: translate(-2px, 2px); }
          40% { transform: translate(2px, -2px); }
          60% { transform: translate(-1px, -1px); }
          80% { transform: translate(1px, 1px); }
        }
        .animate-slideUp { animation: slideUp 0.6s ease-out forwards; }
        .animate-fadeIn { animation: fadeIn 0.4s ease-out forwards; }
        .pulse-glow { animation: pulse-glow 2s ease-in-out infinite; }
        .spin-vinyl { animation: spin-vinyl 3s linear infinite; }
        .glitch { animation: glitch 0.3s ease-in-out; }
        .stagger-1 { animation-delay: 0.1s; opacity: 0; }
        .stagger-2 { animation-delay: 0.2s; opacity: 0; }
        .stagger-3 { animation-delay: 0.3s; opacity: 0; }
        .stagger-4 { animation-delay: 0.4s; opacity: 0; }
        .stagger-5 { animation-delay: 0.5s; opacity: 0; }
      `}</style>

      {/* Noise texture */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.04]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Gradient orb background */}
      <div
        className="pointer-events-none fixed left-1/2 top-1/4 -translate-x-1/2 opacity-20 blur-[120px]"
        style={{
          width: '600px',
          height: '600px',
          background: `radial-gradient(circle, ${tierColors.hex} 0%, transparent 70%)`,
        }}
      />

      <div className="relative z-10">
        {/* Header */}
        <header className={`flex items-center justify-between px-6 py-4 md:px-12 md:py-6 ${mounted ? 'animate-fadeIn' : 'opacity-0'}`}>
          <Link href="/" className="group flex items-center gap-3">
            <div className="relative">
              <Image
                src="/n-logo.png"
                alt="NOiSEMaKER"
                width={48}
                height={48}
                className="h-10 w-10 transition-transform duration-300 group-hover:scale-110 md:h-12 md:w-12"
              />
              <div className={`absolute -inset-1 -z-10 rounded-full opacity-0 blur-xl transition-opacity duration-300 group-hover:opacity-50 ${tierColors.bg}`} />
            </div>
            <span className="text-xl font-black uppercase tracking-tighter text-white md:text-2xl">
              NOiSEMaKER
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <div className={`hidden h-2 w-2 rounded-full md:block ${tierColors.bg}`} />
            <span className="text-xs font-black uppercase tracking-[0.2em] text-gray-500">
              STEP 4 / 4
            </span>
          </div>
        </header>

        {/* Hero Title */}
        <section className={`border-b-4 border-white px-6 py-10 md:py-16 ${mounted ? 'animate-slideUp stagger-1' : 'opacity-0'}`}>
          <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
            <div className="max-w-2xl">
              <p className={`mb-2 text-sm font-bold uppercase tracking-[0.3em] ${tierColors.text}`}>
                Final Step
              </p>
              <h1 className="text-5xl font-black uppercase leading-[0.85] tracking-tighter text-white md:text-7xl lg:text-8xl">
                ADD YOUR
                <br />
                <span className={`${tierColors.text} relative inline-block`}>
                  SONGS
                  <svg className="absolute -bottom-2 left-0 w-full" height="8" viewBox="0 0 200 8">
                    <path d="M0 4 Q50 0, 100 4 T200 4" stroke={tierColors.hex} strokeWidth="3" fill="none" />
                  </svg>
                </span>
              </h1>
              <p className="mt-6 text-base text-gray-400 md:text-lg">
                Drop up to 3 Spotify tracks. We&apos;ll promote them across all your platforms automatically.
              </p>
            </div>

            {/* Progress Badge - Vinyl inspired */}
            <div className={`relative inline-flex items-center gap-4 border-4 ${tierColors.border} bg-black p-4 ${tierColors.glow}`}>
              <div className="relative h-16 w-16">
                <div className={`absolute inset-0 rounded-full ${tierColors.bg} opacity-20 ${validSongCount > 0 ? 'spin-vinyl' : ''}`} />
                <div className="absolute inset-2 rounded-full bg-black" />
                <div className={`absolute inset-[22px] rounded-full ${tierColors.bg}`} />
                <span className={`absolute inset-0 flex items-center justify-center text-2xl font-black ${tierColors.text}`}>
                  {validSongCount}
                </span>
              </div>
              <div className="text-left">
                <p className="text-xs font-bold uppercase tracking-widest text-gray-500">TRACKS</p>
                <p className={`text-lg font-black uppercase ${tierColors.text}`}>
                  {validSongCount === 0 ? 'NONE YET' : validSongCount === 1 ? 'LOADED' : `${validSongCount} LOADED`}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Error */}
        {error && (
          <div className="border-b-4 border-red-500 bg-gradient-to-r from-red-500/20 to-transparent px-6 py-4 animate-fadeIn">
            <div className="flex items-center justify-between">
              <p className="font-bold text-red-400">{error}</p>
              <button onClick={() => setError(null)} className="text-xs text-red-300 underline hover:text-white">
                DISMISS
              </button>
            </div>
          </div>
        )}

        {/* Loading */}
        {isLoading ? (
          <div className="flex items-center justify-center py-32">
            <div className="relative h-20 w-20">
              <div className={`absolute inset-0 rounded-full border-4 ${tierColors.border} opacity-20`} />
              <div className={`absolute inset-0 rounded-full border-4 border-t-transparent ${tierColors.border} animate-spin`} />
            </div>
          </div>
        ) : (
          /* Song Forms */
          <div className="divide-y-2 divide-white/10">
            {SONG_FORMS.map((form, index) => {
              const song = songs[form.id];
              const isValidated = song.isValid && song.validatedData;

              return (
                <div
                  key={form.id}
                  className={`group relative overflow-hidden transition-all duration-500 ${mounted ? `animate-slideUp stagger-${index + 2}` : 'opacity-0'} ${
                    isValidated
                      ? `border-l-4 ${tierColors.border} bg-gradient-to-r ${tierColors.gradient}`
                      : 'hover:bg-white/[0.02]'
                  }`}
                >
                  <div className="px-6 py-8 md:px-12 md:py-10">
                    <div className="flex flex-col gap-6 md:flex-row md:items-start md:gap-8">
                      {/* Number */}
                      <div className="flex flex-col items-start md:items-center">
                        <span className={`text-6xl font-black md:text-7xl ${isValidated ? tierColors.text : 'text-white/10'} transition-colors duration-500`}>
                          0{form.id}
                        </span>
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <h3 className={`text-2xl font-black tracking-tight md:text-3xl ${isValidated ? tierColors.text : 'text-white'} transition-colors duration-300`}>
                          {form.label}
                        </h3>
                        <p className="mb-6 text-sm text-gray-500">{form.sublabel}</p>

                        {isValidated ? (
                          /* Validated Song Card */
                          <div className="space-y-4">
                            <div className={`flex items-center gap-5 rounded-lg border-2 ${tierColors.border} bg-black/50 p-4 backdrop-blur-sm animate-fadeIn`}>
                              {song.validatedData?.album_art_url && (
                                <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg">
                                  <Image
                                    src={song.validatedData.album_art_url}
                                    alt={song.validatedData.name}
                                    fill
                                    className="object-cover"
                                  />
                                  <div className={`absolute inset-0 rounded-lg ring-2 ring-inset ${tierColors.border}`} />
                                </div>
                              )}
                              <div className="flex-1 min-w-0">
                                <p className={`truncate text-lg font-black ${tierColors.text}`}>
                                  {song.validatedData?.name}
                                </p>
                                <p className="truncate text-sm text-gray-400">
                                  {song.validatedData?.artist_name}
                                </p>
                                {song.validatedData?.popularity !== undefined && (
                                  <div className="mt-2 flex items-center gap-2">
                                    <div className="h-1.5 w-24 overflow-hidden rounded-full bg-white/10">
                                      <div
                                        className={`h-full ${tierColors.bg}`}
                                        style={{ width: `${song.validatedData.popularity}%` }}
                                      />
                                    </div>
                                    <span className="text-xs text-gray-500">{song.validatedData.popularity}% popular</span>
                                  </div>
                                )}
                              </div>
                              <button
                                onClick={() => handleClearSong(form.id)}
                                className="flex-shrink-0 rounded border-2 border-white/20 px-4 py-2 text-xs font-black uppercase text-white/50 transition-all hover:border-red-500 hover:bg-red-500/20 hover:text-red-400"
                              >
                                REMOVE
                              </button>
                            </div>

                            {/* Release Date Picker for Song 1 */}
                            {form.requiresReleaseDate && (
                              <div className="animate-fadeIn">
                                <label className="mb-2 block text-xs font-black uppercase tracking-widest text-gray-500">
                                  RELEASE DATE <span className={tierColors.text}>*</span>
                                </label>
                                <input
                                  type="date"
                                  value={song.releaseDate}
                                  onChange={(e) => handleReleaseDateChange(form.id, e.target.value)}
                                  min={getMinReleaseDate()}
                                  className="w-full rounded-lg border-2 border-white/10 bg-black/50 px-5 py-4 text-white backdrop-blur-sm focus:border-white/30 focus:outline-none"
                                />
                                <p className="mt-2 text-xs text-gray-600">When does this track go live? (min. 14 days from today)</p>
                              </div>
                            )}

                            {/* Audio Upload Section (Optional) */}
                            {song.dbSongId && !song.audioSkipped && (
                              <div className="mt-4 rounded-lg border-2 border-white/10 bg-black/30 p-4 animate-fadeIn">
                                {song.audioUploaded && song.audioUrl ? (
                                  /* Waveform Clip Selector */
                                  <div>
                                    <h4 className="mb-3 text-xs font-black uppercase tracking-widest text-white/50">
                                      Select 10-Second Clip
                                    </h4>
                                    <Suspense fallback={
                                      <div className="flex items-center gap-2 py-4">
                                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
                                        <span className="text-xs text-white/40">Loading waveform...</span>
                                      </div>
                                    }>
                                      <AudioClipSelector
                                        songId={song.dbSongId!}
                                        audioUrl={song.audioUrl}
                                        initialClipStart={song.clipStart}
                                        initialClipEnd={song.clipEnd}
                                        onClipSaved={(start, end) => handleClipSaved(form.id, start, end)}
                                      />
                                    </Suspense>
                                    {song.clipSaved && (
                                      <p className="mt-2 text-xs font-bold text-lime-400">
                                        Clip saved! You can adjust it later from your dashboard.
                                      </p>
                                    )}
                                  </div>
                                ) : song.audioUploading ? (
                                  /* Upload Progress */
                                  <div>
                                    <h4 className="mb-2 text-xs font-black uppercase tracking-widest text-white/50">
                                      Uploading Audio...
                                    </h4>
                                    <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                                      <div
                                        className="h-full bg-cyan-400 transition-all"
                                        style={{ width: `${song.audioUploadProgress}%` }}
                                      />
                                    </div>
                                    <p className="mt-1 text-xs text-white/30">{song.audioUploadProgress}%</p>
                                  </div>
                                ) : (
                                  /* Upload Prompt */
                                  <div>
                                    <h4 className="mb-2 text-xs font-black uppercase tracking-widest text-white/50">
                                      Upload Your Song (Optional)
                                    </h4>
                                    <p className="mb-3 text-xs text-white/30">
                                      Upload your audio to select a 10-second promo clip for social media posts.
                                    </p>
                                    <div className="flex items-center gap-3">
                                      <label className={`cursor-pointer border-2 ${tierColors.border} bg-transparent px-4 py-2 text-xs font-black uppercase tracking-wider ${tierColors.text} transition-all hover:bg-white/5`}>
                                        Choose File
                                        <input
                                          type="file"
                                          accept=".mp3,.wav,audio/mpeg,audio/wav"
                                          className="hidden"
                                          onChange={(e) => {
                                            const file = e.target.files?.[0];
                                            if (file) {
                                              if (file.size > 50 * 1024 * 1024) {
                                                setSongs((prev) => ({
                                                  ...prev,
                                                  [form.id]: { ...prev[form.id], error: 'File too large (max 50MB)' },
                                                }));
                                                return;
                                              }
                                              handleAudioUpload(form.id, file);
                                            }
                                          }}
                                        />
                                      </label>
                                      <button
                                        onClick={() => handleSkipAudio(form.id)}
                                        className="text-xs text-white/30 underline hover:text-white/50"
                                      >
                                        Skip for now
                                      </button>
                                    </div>
                                    <p className="mt-2 text-xs text-white/20">
                                      MP3 or WAV, max 50MB
                                    </p>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Audio skipped message */}
                            {song.audioSkipped && (
                              <p className="mt-2 text-xs text-white/30 animate-fadeIn">
                                You can add audio later from your dashboard.
                              </p>
                            )}
                          </div>
                        ) : (
                          /* Input Form */
                          <div className="space-y-4">
                            <div className="relative">
                              <input
                                type="url"
                                value={song.url}
                                onChange={(e) => handleUrlChange(form.id, e.target.value)}
                                placeholder="Paste Spotify track URL..."
                                className={`w-full rounded-lg border-2 bg-black/50 px-5 py-4 text-white placeholder-gray-600 backdrop-blur-sm transition-all focus:outline-none ${
                                  song.error
                                    ? 'border-red-500/50 focus:border-red-500'
                                    : 'border-white/10 focus:border-white/30'
                                }`}
                              />
                              {song.isValidating && (
                                <div className="absolute right-4 top-1/2 -translate-y-1/2">
                                  <div className={`h-6 w-6 rounded-full border-2 border-t-transparent ${tierColors.border} animate-spin`} />
                                </div>
                              )}
                            </div>

                            {song.error && (
                              <p className="flex items-center gap-2 text-sm text-red-400">
                                <span className="text-red-500">✕</span> {song.error}
                              </p>
                            )}

                            {form.requiresReleaseDate && song.isValid && (
                              <div className="animate-fadeIn">
                                <label className="mb-2 block text-xs font-black uppercase tracking-widest text-gray-500">
                                  RELEASE DATE <span className={tierColors.text}>*</span>
                                </label>
                                <input
                                  type="date"
                                  value={song.releaseDate}
                                  onChange={(e) => handleReleaseDateChange(form.id, e.target.value)}
                                  min={getMinReleaseDate()}
                                  className={`w-full rounded-lg border-2 border-white/10 bg-black/50 px-5 py-4 text-white backdrop-blur-sm focus:border-white/30 focus:outline-none`}
                                />
                                <p className="mt-2 text-xs text-gray-600">Must be at least 14 days from today</p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Status */}
                      <div className="flex items-start">
                        {isValidated ? (
                          <div className={`flex items-center gap-2 rounded-full px-5 py-2 ${tierColors.bg} text-sm font-black uppercase text-black pulse-glow`}>
                            <span>✓</span> ADDED
                          </div>
                        ) : song.isValidating ? (
                          <div className="rounded-full border-2 border-white/20 px-5 py-2 text-xs font-black uppercase text-gray-500">
                            CHECKING...
                          </div>
                        ) : song.url ? (
                          <div className="rounded-full border-2 border-white/10 px-5 py-2 text-xs font-black uppercase text-gray-600">
                            INVALID
                          </div>
                        ) : (
                          <div className="rounded-full border-2 border-dashed border-white/10 px-5 py-2 text-xs font-black uppercase text-white/20">
                            OPTIONAL
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}


        {/* Continue Button */}
        <section className="sticky bottom-0 border-t-4 border-white bg-black/95 px-6 py-5 backdrop-blur-lg">
          <button
            onClick={handleContinue}
            disabled={!canContinue || isSubmitting || song1NeedsReleaseDate}
            className={`group relative w-full overflow-hidden rounded-lg border-4 py-5 text-lg font-black uppercase tracking-wider transition-all duration-300 ${
              canContinue && !isSubmitting && !song1NeedsReleaseDate
                ? `${tierColors.border} bg-white text-black hover:scale-[1.02] hover:${tierColors.glow}`
                : 'cursor-not-allowed border-gray-800 bg-gray-900 text-gray-600'
            }`}
          >
            {canContinue && !isSubmitting && !song1NeedsReleaseDate && (
              <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700`} />
            )}
            <span className="relative">
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-3">
                  <div className="h-5 w-5 rounded-full border-2 border-gray-600 border-t-transparent animate-spin" />
                  LOADING TRACKS...
                </span>
              ) : !canContinue ? (
                'ADD AT LEAST 1 TRACK'
              ) : song1NeedsReleaseDate ? (
                'ENTER RELEASE DATE'
              ) : (
                `LET'S GO → ${validSongCount} TRACK${validSongCount > 1 ? 'S' : ''} READY`
              )}
            </span>
          </button>
        </section>

        {/* Footer */}
        <footer className="border-t-2 border-white/10 bg-black px-6 py-8 text-center">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-gray-700">
            © 2026 NOiSEMaKER by DooWopp
          </p>
        </footer>
      </div>
    </main>
  );
}

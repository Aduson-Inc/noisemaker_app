'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { frankGarageAPI } from '@/lib/api';
import type {
  FrankArtwork,
  FrankArtCollectionItem,
} from '@/types';

/**
 * FRANK'S GARAGE - AI Art Marketplace
 *
 * Gen Z Bold design following the NOiSEMaKER aesthetic
 * - Browse AI-generated artwork
 * - FREE download (1 token, art stays in pool)
 * - PURCHASE ($2.99-$19.99, art removed from pool)
 * - 5-minute hold system for previewing
 */

type FilterType = 'all' | 'new' | 'popular' | 'exclusive';
type ViewMode = 'gallery' | 'collection';
type PurchaseType = 'single' | 'bundle_5' | 'bundle_15';

const PRICING = {
  single: { count: 1, amount: 299, label: '$2.99' },
  bundle_5: { count: 5, amount: 999, label: '$9.99' },
  bundle_15: { count: 15, amount: 1999, label: '$19.99' },
};

export default function FranksGarage() {
  // Auth
  const [userId, setUserId] = useState<string | null>(null);

  // View state
  const [viewMode, setViewMode] = useState<ViewMode>('gallery');
  const [filter, setFilter] = useState<FilterType>('all');

  // Data
  const [artwork, setArtwork] = useState<FrankArtwork[]>([]);
  const [collection, setCollection] = useState<FrankArtCollectionItem[]>([]);
  const [tokens, setTokens] = useState<number>(0);
  const [totalArtwork, setTotalArtwork] = useState<number>(0);

  // Selection mode
  const [selectMode, setSelectMode] = useState<boolean>(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // Preview modal
  const [previewArtwork, setPreviewArtwork] = useState<FrankArtwork | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [holdExpiresAt, setHoldExpiresAt] = useState<Date | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);

  // Loading/error states
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [isPurchasing, setIsPurchasing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Long press detection
  const longPressTimer = useRef<NodeJS.Timeout | null>(null);
  const [longPressTarget, setLongPressTarget] = useState<string | null>(null);

  // Initialize - get user ID from localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          setUserId(payload.user_id);
        } catch {
          setUserId(null);
        }
      }
    }
  }, []);

  // Load artwork when filter changes
  const loadArtwork = useCallback(async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await frankGarageAPI.getArtwork(filter, userId);
      if (response.data.success) {
        setArtwork(response.data.artwork || []);
        setTotalArtwork(response.data.total || 0);
      }
    } catch (err) {
      console.error('Error loading artwork:', err);
      setError('Failed to load artwork');
    } finally {
      setIsLoading(false);
    }
  }, [userId, filter]);

  // Load collection
  const loadCollection = useCallback(async () => {
    if (!userId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await frankGarageAPI.getMyCollection(userId);
      if (response.data.success) {
        setCollection(response.data.collection || []);
      }
    } catch (err) {
      console.error('Error loading collection:', err);
      setError('Failed to load collection');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Load tokens
  const loadTokens = useCallback(async () => {
    if (!userId) return;

    try {
      const response = await frankGarageAPI.getTokens(userId);
      if (response.data.success) {
        setTokens(response.data.art_tokens || 0);
      }
    } catch (err) {
      console.error('Error loading tokens:', err);
    }
  }, [userId]);

  // Initial load
  useEffect(() => {
    if (userId) {
      loadTokens();
      if (viewMode === 'gallery') {
        loadArtwork();
      } else {
        loadCollection();
      }
    }
  }, [userId, viewMode, loadArtwork, loadCollection, loadTokens]);

  // Reload artwork when filter changes
  useEffect(() => {
    if (userId && viewMode === 'gallery') {
      loadArtwork();
    }
  }, [filter, userId, viewMode, loadArtwork]);

  // Hold timer countdown
  useEffect(() => {
    if (!holdExpiresAt) return;

    const interval = setInterval(() => {
      const now = new Date();
      const remaining = Math.max(0, Math.floor((holdExpiresAt.getTime() - now.getTime()) / 1000));
      setTimeRemaining(remaining);

      if (remaining === 0) {
        // Hold expired
        setPreviewArtwork(null);
        setPreviewUrl(null);
        setHoldExpiresAt(null);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [holdExpiresAt]);

  // Handle long press start
  const handleTouchStart = (artworkId: string) => {
    if (selectMode) return; // In select mode, use tap instead

    longPressTimer.current = setTimeout(() => {
      setLongPressTarget(artworkId);
      handleOpenPreview(artworkId);
    }, 500);
  };

  // Handle long press end
  const handleTouchEnd = () => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }
    setLongPressTarget(null);
  };

  // Handle tap in select mode
  const handleTap = (artworkId: string) => {
    if (!selectMode) {
      // Enter select mode on first tap if not in preview
      setSelectMode(true);
      setSelectedIds(new Set([artworkId]));
    } else {
      // Toggle selection
      const newSelected = new Set(selectedIds);
      if (newSelected.has(artworkId)) {
        newSelected.delete(artworkId);
      } else {
        newSelected.add(artworkId);
      }
      setSelectedIds(newSelected);

      // Exit select mode if nothing selected
      if (newSelected.size === 0) {
        setSelectMode(false);
      }
    }
  };

  // Open preview modal with hold
  const handleOpenPreview = async (artworkId: string) => {
    if (!userId) return;

    const art = artwork.find((a) => a.artwork_id === artworkId);
    if (!art) return;

    try {
      const response = await frankGarageAPI.placeHold(userId, artworkId);
      if (response.data.success) {
        setPreviewArtwork(art);
        setPreviewUrl(response.data.mobile_url);
        setHoldExpiresAt(new Date(response.data.expires_at));
      }
    } catch (err) {
      console.error('Error placing hold:', err);
      setError('Failed to preview artwork');
    }
  };

  // Close preview and release hold
  const handleClosePreview = async () => {
    if (previewArtwork) {
      try {
        await frankGarageAPI.releaseHold(previewArtwork.artwork_id);
      } catch {
        // Ignore release errors
      }
    }

    setPreviewArtwork(null);
    setPreviewUrl(null);
    setHoldExpiresAt(null);
    setTimeRemaining(0);
  };

  // Free download (1 token)
  const handleFreeDownload = async () => {
    if (!userId || !previewArtwork || tokens < 1) return;

    setIsDownloading(true);
    setError(null);

    try {
      const response = await frankGarageAPI.downloadFree(userId, previewArtwork.artwork_id);
      if (response.data.success) {
        // Update tokens
        setTokens(response.data.tokens_remaining);

        // Trigger download
        const link = document.createElement('a');
        link.href = response.data.download_url;
        link.download = `frank-art-${previewArtwork.artwork_id}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Close preview
        handleClosePreview();

        // Reload artwork to update download counts
        loadArtwork();
      }
    } catch (err) {
      console.error('Error downloading:', err);
      setError('Failed to download artwork');
    } finally {
      setIsDownloading(false);
    }
  };

  // Purchase artwork (money only, no tokens)
  const handlePurchase = async (purchaseType: PurchaseType) => {
    if (!userId) return;

    const artworkIds = selectMode
      ? Array.from(selectedIds)
      : previewArtwork
        ? [previewArtwork.artwork_id]
        : [];

    if (artworkIds.length === 0) return;

    setIsPurchasing(true);
    setError(null);

    try {
      const response = await frankGarageAPI.createPaymentIntent(userId, artworkIds, purchaseType);
      if (response.data.success) {
        // In a real implementation, you'd integrate Stripe Elements here
        // For now, we'll show a placeholder
        alert(`Stripe checkout would open here for ${PRICING[purchaseType].label}`);

        // After successful payment, call confirmPurchase
        // const confirmResponse = await frankGarageAPI.confirmPurchase(response.data.payment_intent_id);
      }
    } catch (err) {
      console.error('Error creating payment:', err);
      setError('Failed to start purchase');
    } finally {
      setIsPurchasing(false);
    }
  };

  // Format time remaining as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Cancel selection mode
  const handleCancelSelect = () => {
    setSelectMode(false);
    setSelectedIds(new Set());
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

          {/* Token Balance */}
          <div className="flex items-center gap-4">
            <div className="border-2 border-lime-400 bg-lime-400/10 px-4 py-2">
              <span className="text-xs font-bold uppercase tracking-wider text-lime-400">
                TOKENS
              </span>
              <span className="ml-2 text-2xl font-black text-lime-400">{tokens}</span>
            </div>

            <Link
              href="/dashboard"
              className="border-2 border-white bg-transparent px-4 py-2 text-sm font-black uppercase tracking-widest text-white transition-all hover:bg-white hover:text-black"
            >
              Back
            </Link>
          </div>
        </header>

        {/* Title */}
        <section className="border-b-4 border-fuchsia-500 bg-fuchsia-500 px-4 py-6 md:px-8 md:py-8">
          <div className="mx-auto max-w-7xl">
            <h1 className="text-4xl font-black uppercase leading-none tracking-tighter text-black md:text-6xl lg:text-7xl">
              FRANK&apos;S GARAGE
            </h1>
            <p className="mt-2 text-sm font-bold uppercase tracking-wider text-black/70">
              AI-Generated Album Art • {totalArtwork} Available
            </p>
          </div>
        </section>

        {/* View Toggle + Filters */}
        <section className="border-b-2 border-white/20 bg-black px-4 py-4 md:px-8">
          <div className="mx-auto flex max-w-7xl flex-col gap-4 md:flex-row md:items-center md:justify-between">
            {/* View Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('gallery')}
                className={`border-2 px-4 py-2 text-sm font-black uppercase transition-all ${
                  viewMode === 'gallery'
                    ? 'border-fuchsia-500 bg-fuchsia-500 text-black'
                    : 'border-white/30 text-white/50 hover:border-white hover:text-white'
                }`}
              >
                Gallery
              </button>
              <button
                onClick={() => setViewMode('collection')}
                className={`border-2 px-4 py-2 text-sm font-black uppercase transition-all ${
                  viewMode === 'collection'
                    ? 'border-cyan-400 bg-cyan-400 text-black'
                    : 'border-white/30 text-white/50 hover:border-white hover:text-white'
                }`}
              >
                My Collection
              </button>
            </div>

            {/* Filters (Gallery only) */}
            {viewMode === 'gallery' && (
              <div className="flex gap-2 overflow-x-auto">
                {(['all', 'new', 'popular', 'exclusive'] as FilterType[]).map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`whitespace-nowrap border-2 px-3 py-1 text-xs font-black uppercase transition-all ${
                      filter === f
                        ? 'border-lime-400 bg-lime-400 text-black'
                        : 'border-white/30 text-white/50 hover:border-lime-400 hover:text-lime-400'
                    }`}
                  >
                    {f === 'all' && 'All'}
                    {f === 'new' && 'New (7d)'}
                    {f === 'popular' && 'Popular (5+)'}
                    {f === 'exclusive' && 'Exclusive (0)'}
                  </button>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Selection Mode Bar */}
        {selectMode && (
          <section className="border-b-4 border-cyan-400 bg-cyan-400/20 px-4 py-3 md:px-8">
            <div className="mx-auto flex max-w-7xl items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-xl font-black text-cyan-400">{selectedIds.size}</span>
                <span className="text-sm font-bold uppercase text-cyan-400">Selected</span>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleCancelSelect}
                  className="border-2 border-white/50 px-3 py-1 text-xs font-black uppercase text-white hover:border-white"
                >
                  Cancel
                </button>

                {selectedIds.size === 1 && (
                  <button
                    onClick={() => handlePurchase('single')}
                    disabled={isPurchasing}
                    className="border-2 border-fuchsia-500 bg-fuchsia-500 px-3 py-1 text-xs font-black uppercase text-black hover:bg-fuchsia-400"
                  >
                    Buy 1 - $2.99
                  </button>
                )}

                {selectedIds.size >= 5 && selectedIds.size < 15 && (
                  <button
                    onClick={() => handlePurchase('bundle_5')}
                    disabled={isPurchasing}
                    className="border-2 border-lime-400 bg-lime-400 px-3 py-1 text-xs font-black uppercase text-black hover:bg-lime-300"
                  >
                    Buy 5 - $9.99
                  </button>
                )}

                {selectedIds.size >= 15 && (
                  <button
                    onClick={() => handlePurchase('bundle_15')}
                    disabled={isPurchasing}
                    className="border-2 border-cyan-400 bg-cyan-400 px-3 py-1 text-xs font-black uppercase text-black hover:bg-cyan-300"
                  >
                    Buy 15 - $19.99
                  </button>
                )}
              </div>
            </div>
          </section>
        )}

        {/* Error Message */}
        {error && (
          <section className="border-b-4 border-red-500 bg-red-500/20 px-4 py-3 md:px-8">
            <div className="mx-auto flex max-w-7xl items-center justify-between">
              <p className="text-sm font-bold text-red-400">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-xs font-bold text-red-300 underline hover:text-white"
              >
                Dismiss
              </button>
            </div>
          </section>
        )}

        {/* Main Content */}
        <section className="px-4 py-6 md:px-8 md:py-8">
          <div className="mx-auto max-w-7xl">
            {isLoading ? (
              <div className="flex items-center justify-center py-20">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-fuchsia-500 border-t-transparent" />
              </div>
            ) : viewMode === 'gallery' ? (
              /* Gallery Grid */
              <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8">
                {artwork.map((art) => {
                  const isSelected = selectedIds.has(art.artwork_id);
                  const isHeld = art.held_by && art.held_by !== userId;

                  return (
                    <div
                      key={art.artwork_id}
                      className={`group relative aspect-square cursor-pointer overflow-hidden border-2 transition-all ${
                        isSelected
                          ? 'border-cyan-400 ring-2 ring-cyan-400'
                          : isHeld
                            ? 'border-red-500/50 opacity-50'
                            : 'border-white/20 hover:border-fuchsia-500'
                      }`}
                      onClick={() => !isHeld && handleTap(art.artwork_id)}
                      onTouchStart={() => !isHeld && handleTouchStart(art.artwork_id)}
                      onTouchEnd={handleTouchEnd}
                      onMouseDown={() => !isHeld && handleTouchStart(art.artwork_id)}
                      onMouseUp={handleTouchEnd}
                      onMouseLeave={handleTouchEnd}
                    >
                      <img
                        src={art.thumbnail_url}
                        alt={`Art ${art.artwork_id}`}
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />

                      {/* Selection overlay */}
                      {isSelected && (
                        <div className="absolute inset-0 flex items-center justify-center bg-cyan-400/30">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-400 text-lg font-black text-black">
                            ✓
                          </div>
                        </div>
                      )}

                      {/* Held by another user */}
                      {isHeld && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black/70">
                          <span className="text-xs font-bold text-red-400">HELD</span>
                        </div>
                      )}

                      {/* Download count badge */}
                      <div className="absolute bottom-1 right-1 rounded bg-black/70 px-1.5 py-0.5 text-xs font-bold text-white">
                        {art.download_count}
                      </div>

                      {/* Long press indicator */}
                      {longPressTarget === art.artwork_id && (
                        <div className="absolute inset-0 flex items-center justify-center bg-fuchsia-500/30">
                          <div className="h-8 w-8 animate-ping rounded-full bg-fuchsia-500" />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              /* Collection Grid */
              <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8">
                {collection.length === 0 ? (
                  <div className="col-span-full py-20 text-center">
                    <p className="text-xl font-black uppercase text-white/50">No artwork yet</p>
                    <p className="mt-2 text-sm text-white/30">
                      Download or purchase artwork to build your collection
                    </p>
                  </div>
                ) : (
                  collection.map((item) => (
                    <div
                      key={item.artwork_id}
                      className={`group relative aspect-square overflow-hidden border-2 ${
                        item.type === 'purchase' ? 'border-fuchsia-500' : 'border-lime-400/50'
                      }`}
                    >
                      <img
                        src={item.thumbnail_url}
                        alt={`Collection ${item.artwork_id}`}
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />

                      {/* Type badge */}
                      <div
                        className={`absolute bottom-1 right-1 rounded px-1.5 py-0.5 text-xs font-bold ${
                          item.type === 'purchase'
                            ? 'bg-fuchsia-500 text-black'
                            : 'bg-lime-400/20 text-lime-400'
                        }`}
                      >
                        {item.type === 'purchase' ? 'OWNED' : 'FREE'}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Empty Gallery State */}
            {viewMode === 'gallery' && artwork.length === 0 && !isLoading && (
              <div className="py-20 text-center">
                <p className="text-xl font-black uppercase text-white/50">No artwork found</p>
                <p className="mt-2 text-sm text-white/30">Try a different filter or check back later</p>
              </div>
            )}
          </div>
        </section>

        {/* How It Works */}
        <section className="border-t-4 border-white/20 bg-black px-4 py-8 md:px-8">
          <div className="mx-auto max-w-7xl">
            <h2 className="mb-6 text-sm font-black uppercase tracking-widest text-white/50">
              How It Works
            </h2>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="border-2 border-lime-400 p-4">
                <div className="text-3xl font-black text-lime-400">FREE</div>
                <div className="mt-1 text-sm font-bold text-white">1 Token per Download</div>
                <p className="mt-2 text-xs text-white/50">
                  Use your tokens to download art for free. Art stays available for others.
                </p>
              </div>
              <div className="border-2 border-fuchsia-500 p-4">
                <div className="text-3xl font-black text-fuchsia-500">BUY</div>
                <div className="mt-1 text-sm font-bold text-white">$2.99 - $19.99</div>
                <p className="mt-2 text-xs text-white/50">
                  Purchase to own exclusively. Art is removed from the pool permanently.
                </p>
              </div>
              <div className="border-2 border-cyan-400 p-4">
                <div className="text-3xl font-black text-cyan-400">EARN</div>
                <div className="mt-1 text-sm font-bold text-white">+3 Tokens per Song</div>
                <p className="mt-2 text-xs text-white/50">
                  Upload songs to earn tokens. Start with 3, earn up to 12 more.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t-4 border-white bg-black px-4 py-6 text-center md:px-8">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-600">
            Frank&apos;s Garage by NOiSEMaKER
          </p>
        </footer>
      </div>

      {/* Preview Modal */}
      {previewArtwork && previewUrl && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 p-4"
          onClick={handleClosePreview}
        >
          <div
            className="relative w-full max-w-lg"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Timer */}
            <div className="absolute -top-12 left-0 right-0 text-center">
              <span className="text-sm font-bold uppercase text-white/50">Hold expires in </span>
              <span
                className={`text-lg font-black ${
                  timeRemaining < 60 ? 'text-red-400' : 'text-lime-400'
                }`}
              >
                {formatTime(timeRemaining)}
              </span>
            </div>

            {/* Image */}
            <div className="aspect-square overflow-hidden border-4 border-white">
              <img
                src={previewUrl}
                alt="Preview"
                className="h-full w-full object-cover"
              />
            </div>

            {/* Art Info */}
            <div className="mt-4 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase text-white/50">
                  {previewArtwork.art_style} • {previewArtwork.artist_style}
                </p>
                <p className="text-xs text-white/30">
                  {previewArtwork.download_count} downloads
                </p>
              </div>
              <button
                onClick={handleClosePreview}
                className="text-sm font-bold text-white/50 hover:text-white"
              >
                Close
              </button>
            </div>

            {/* Actions */}
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {/* Free Download */}
              <button
                onClick={handleFreeDownload}
                disabled={isDownloading || tokens < 1}
                className={`border-4 py-4 text-center font-black uppercase transition-all ${
                  tokens >= 1
                    ? 'border-lime-400 bg-lime-400 text-black hover:bg-lime-300'
                    : 'cursor-not-allowed border-white/20 bg-white/10 text-white/30'
                }`}
              >
                {isDownloading ? (
                  'Downloading...'
                ) : tokens >= 1 ? (
                  <>
                    Download Free
                    <span className="ml-2 text-xs">(1 Token)</span>
                  </>
                ) : (
                  'No Tokens'
                )}
              </button>

              {/* Purchase */}
              <button
                onClick={() => handlePurchase('single')}
                disabled={isPurchasing}
                className="border-4 border-fuchsia-500 bg-fuchsia-500 py-4 text-center font-black uppercase text-black transition-all hover:bg-fuchsia-400"
              >
                {isPurchasing ? 'Processing...' : 'Buy Exclusive - $2.99'}
              </button>
            </div>

            <p className="mt-3 text-center text-xs text-white/30">
              Free: Art stays in pool • Buy: Art removed permanently
            </p>
          </div>
        </div>
      )}
    </main>
  );
}

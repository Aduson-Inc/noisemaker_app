'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Post } from '@/types';
import { dashboardAPI } from '@/lib/api';

interface PostReviewModalProps {
  post: Post | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

export default function PostReviewModal({ post, isOpen, onClose, onUpdate }: PostReviewModalProps) {
  const [caption, setCaption] = useState(post?.caption || '');
  const [loading, setLoading] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  if (!post) return null;

  // Check if post can be edited (more than 1 hour before scheduled time)
  const scheduledTime = new Date(post.scheduled_time);
  const now = new Date();
  const hoursUntilPost = (scheduledTime.getTime() - now.getTime()) / (1000 * 60 * 60);
  const canEdit = hoursUntilPost > 1;

  const handleEditCaption = async () => {
    if (!canEdit || caption === post.caption) return;

    setLoading(true);
    try {
      await dashboardAPI.updateCaption(post.post_id, caption);
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to update caption:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    setLoading(true);
    try {
      await dashboardAPI.approvePost(post.post_id);
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to approve post:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    try {
      await dashboardAPI.rejectPost(post.post_id);
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to reject post:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="glass p-6 rounded-xl border border-slate-700 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-2xl font-bold text-white">Post Preview</h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white text-2xl transition-colors"
              >
                ×
              </button>
            </div>

            {/* Post Image */}
            <div className="mb-6 rounded-lg overflow-hidden bg-slate-800">
              {post.image_url ? (
                <img
                  src={post.image_url}
                  alt="Post preview"
                  className="w-full h-auto"
                />
              ) : (
                <div className="w-full h-64 flex items-center justify-center text-gray-500">
                  No image available
                </div>
              )}
            </div>

            {/* Caption */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Caption
              </label>
              <textarea
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                disabled={!canEdit || loading}
                className={`
                  w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white
                  focus:outline-none focus:border-purple-500 transition-colors
                  ${!canEdit ? 'opacity-50 cursor-not-allowed' : ''}
                `}
                rows={4}
              />
              {!canEdit && (
                <p className="text-amber-400 text-xs mt-2">
                  Caption cannot be edited less than 1 hour before scheduled time
                </p>
              )}
            </div>

            {/* Scheduled Time */}
            <div className="mb-6 text-gray-400 text-sm">
              <span className="font-semibold">Scheduled for:</span>{' '}
              {scheduledTime.toLocaleString()}
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleEditCaption}
                disabled={!canEdit || caption === post.caption || loading}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Saving...' : 'Edit Caption'}
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleApprove}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Processing...' : 'Approve'}
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowConfirm(true)}
                disabled={loading}
                className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Reject
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onClose}
                disabled={loading}
                className="bg-slate-700 hover:bg-slate-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                Close
              </motion.button>
            </div>

            {/* Confirmation Dialog */}
            {showConfirm && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-xl"
              >
                <div className="bg-slate-800 p-6 rounded-lg max-w-sm mx-4">
                  <h3 className="text-white font-bold mb-2">Are you sure?</h3>
                  <p className="text-gray-300 text-sm mb-4">
                    This will reject the post and it won't be published.
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={handleReject}
                      className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                      Yes, Reject
                    </button>
                    <button
                      onClick={() => setShowConfirm(false)}
                      className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

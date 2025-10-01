import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { ArrowLeft, Lightbulb, TrendingUp, Send, Heart, MessageCircle, Users, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const IdeaBoard = () => {
  const [ideas, setIdeas] = useState([]);
  const [newIdea, setNewIdea] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [upvotingIds, setUpvotingIds] = useState(new Set());
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isPolling, setIsPolling] = useState(true);

  const characterLimit = 280;
  const remainingChars = characterLimit - newIdea.length;

  // Fetch ideas from the API
  const fetchIdeas = async (showLoadingSpinner = false) => {
    try {
      if (showLoadingSpinner) setIsLoading(true);
      const response = await axios.get(`${API}/ideas`);
      setIdeas(response.data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching ideas:', error);
      toast.error('Failed to load ideas. Please try again.');
    } finally {
      if (showLoadingSpinner) setIsLoading(false);
    }
  };

  // Submit a new idea
  const submitIdea = async (e) => {
    e.preventDefault();
    if (!newIdea.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await axios.post(`${API}/ideas`, { text: newIdea.trim() });
      setNewIdea('');
      await fetchIdeas(); // Refresh the list
      toast.success('Your idea has been shared! 🎉');
    } catch (error) {
      console.error('Error submitting idea:', error);
      toast.error('Failed to submit idea. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Upvote an idea
  const upvoteIdea = async (ideaId) => {
    if (upvotingIds.has(ideaId)) return;

    setUpvotingIds(prev => new Set([...prev, ideaId]));
    try {
      await axios.patch(`${API}/ideas/${ideaId}/upvote`);
      await fetchIdeas(); // Refresh to get updated counts
      toast.success('Upvoted! ❤️');
    } catch (error) {
      console.error('Error upvoting idea:', error);
      toast.error('Failed to upvote. Please try again.');
    } finally {
      setUpvotingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(ideaId);
        return newSet;
      });
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now - date) / (1000 * 60));
      return diffInMinutes < 1 ? 'Just now' : `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  useEffect(() => {
    // Initial load with spinner
    fetchIdeas(true);
    
    // Set up periodic polling for real-time updates from other users
    const pollInterval = setInterval(() => {
      // Silent polling - don't show loading spinner for background updates
      fetchIdeas(false);
    }, 5000); // Poll every 5 seconds for live updates
    
    // Cleanup interval on component unmount
    return () => {
      clearInterval(pollInterval);
      setIsPolling(false);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link to="/" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors">
                <ArrowLeft className="w-5 h-5" />
                <span className="font-medium">Back to Home</span>
              </Link>
              <div className="hidden sm:block w-px h-6 bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Lightbulb className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-gray-900">Idea Board</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge className="bg-green-100 text-green-800 px-3 py-1 rounded-full font-medium border-0">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                Live
              </Badge>
              <span className="text-sm text-gray-600">{ideas.length} ideas shared</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Share Your
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Ideas</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-6">
            Welcome to the idea board! Share your thoughts, discover amazing concepts, and help the best ideas rise to the top.
          </p>
        </div>

        {/* Idea Submission Form */}
        <Card className="mb-8 border-0 shadow-xl bg-white">
          <CardHeader className="pb-4">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">What's your idea?</h2>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={submitIdea}>
              <div className="space-y-4">
                <div>
                  <Textarea
                    data-testid="idea-input"
                    placeholder="Share your brilliant idea... (max 280 characters)"
                    value={newIdea}
                    onChange={(e) => setNewIdea(e.target.value)}
                    maxLength={characterLimit}
                    rows={4}
                    className="idea-input resize-none border-2 border-gray-200 focus:border-blue-500 transition-colors"
                  />
                  <div className={`character-count mt-2 text-sm ${
                    remainingChars < 20 ? (remainingChars < 0 ? 'text-red-500' : 'text-yellow-500') : 'text-gray-500'
                  }`}>
                    {remainingChars} characters remaining
                  </div>
                </div>
                <Button
                  data-testid="submit-idea-btn"
                  type="submit"
                  disabled={!newIdea.trim() || isSubmitting || remainingChars < 0}
                  className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-lg font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:transform-none disabled:hover:shadow-none"
                >
                  {isSubmitting ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Sharing...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Send className="w-4 h-4" />
                      <span>Share Idea</span>
                    </div>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Ideas Grid */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">Top Ideas</h2>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Users className="w-4 h-4" />
              <span>Sorted by community votes</span>
            </div>
          </div>

          {isLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, index) => (
                <Card key={index} className="idea-card border-0 shadow-lg">
                  <CardContent className="p-6">
                    <div className="loading-skeleton h-4 rounded mb-3"></div>
                    <div className="loading-skeleton h-16 rounded mb-4"></div>
                    <div className="flex justify-between items-center">
                      <div className="loading-skeleton h-8 w-20 rounded-full"></div>
                      <div className="loading-skeleton h-4 w-16 rounded"></div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : ideas.length === 0 ? (
            <Card className="border-0 shadow-lg bg-white text-center py-12">
              <CardContent>
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MessageCircle className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No ideas yet!</h3>
                <p className="text-gray-600">Be the first to share an idea and get the conversation started.</p>
              </CardContent>
            </Card>
          ) : (
            <div data-testid="ideas-grid" className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {ideas.map((idea) => (
                <Card key={idea.id} className="idea-card border-0 shadow-lg bg-white hover:shadow-xl transition-all duration-300">
                  <CardContent className="p-6">
                    <div className="mb-4">
                      <p className="text-gray-800 text-base leading-relaxed">{idea.text}</p>
                    </div>
                    <div className="flex justify-between items-center">
                      <Button
                        data-testid={`upvote-btn-${idea.id}`}
                        onClick={() => upvoteIdea(idea.id)}
                        disabled={upvotingIds.has(idea.id)}
                        className="bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white px-4 py-2 rounded-full font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:transform-none"
                        size="sm"
                      >
                        {upvotingIds.has(idea.id) ? (
                          <div className="flex items-center space-x-1">
                            <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            <span>{idea.upvotes}</span>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-1">
                            <Heart className="w-4 h-4" />
                            <span>{idea.upvotes}</span>
                          </div>
                        )}
                      </Button>
                      <span className="text-sm text-gray-500">
                        {formatDate(idea.created_at)}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default IdeaBoard;

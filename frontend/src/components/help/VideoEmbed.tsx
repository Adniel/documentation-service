/**
 * VideoEmbed - Responsive video player with YouTube/Vimeo detection.
 *
 * Automatically converts YouTube and Vimeo URLs into embed iframes.
 * Falls back to a native <video> element for other sources.
 */

interface VideoEmbedProps {
  src: string;
  title: string;
  aspectRatio?: string;
}

/**
 * Extract a YouTube video ID from various URL formats:
 * - https://www.youtube.com/watch?v=VIDEO_ID
 * - https://youtu.be/VIDEO_ID
 * - https://www.youtube.com/embed/VIDEO_ID
 */
function getYouTubeId(url: string): string | null {
  try {
    const parsed = new URL(url);
    if (
      parsed.hostname === 'www.youtube.com' ||
      parsed.hostname === 'youtube.com'
    ) {
      if (parsed.pathname.startsWith('/embed/')) {
        return parsed.pathname.split('/embed/')[1]?.split('/')[0] || null;
      }
      return parsed.searchParams.get('v');
    }
    if (parsed.hostname === 'youtu.be') {
      return parsed.pathname.slice(1).split('/')[0] || null;
    }
  } catch {
    // invalid URL
  }
  return null;
}

/**
 * Extract a Vimeo video ID from URLs like:
 * - https://vimeo.com/VIDEO_ID
 * - https://player.vimeo.com/video/VIDEO_ID
 */
function getVimeoId(url: string): string | null {
  try {
    const parsed = new URL(url);
    if (parsed.hostname === 'vimeo.com') {
      const segments = parsed.pathname.split('/').filter(Boolean);
      const id = segments[0];
      return id && /^\d+$/.test(id) ? id : null;
    }
    if (parsed.hostname === 'player.vimeo.com') {
      const segments = parsed.pathname.split('/').filter(Boolean);
      // /video/VIDEO_ID
      const idx = segments.indexOf('video');
      if (idx !== -1 && segments[idx + 1]) {
        return segments[idx + 1];
      }
    }
  } catch {
    // invalid URL
  }
  return null;
}

export function VideoEmbed({
  src,
  title,
  aspectRatio = '16/9',
}: VideoEmbedProps) {
  const youtubeId = getYouTubeId(src);
  const vimeoId = !youtubeId ? getVimeoId(src) : null;

  const containerStyle = { aspectRatio };

  if (youtubeId) {
    return (
      <div
        className="w-full rounded-lg overflow-hidden bg-black"
        style={containerStyle}
      >
        <iframe
          src={`https://www.youtube.com/embed/${youtubeId}`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="w-full h-full border-0"
        />
      </div>
    );
  }

  if (vimeoId) {
    return (
      <div
        className="w-full rounded-lg overflow-hidden bg-black"
        style={containerStyle}
      >
        <iframe
          src={`https://player.vimeo.com/video/${vimeoId}`}
          title={title}
          allow="autoplay; fullscreen; picture-in-picture"
          allowFullScreen
          className="w-full h-full border-0"
        />
      </div>
    );
  }

  // Fallback: native video element
  return (
    <div
      className="w-full rounded-lg overflow-hidden bg-black"
      style={containerStyle}
    >
      <video
        src={src}
        title={title}
        controls
        className="w-full h-full"
      >
        <track kind="captions" />
        Your browser does not support the video element.
      </video>
    </div>
  );
}

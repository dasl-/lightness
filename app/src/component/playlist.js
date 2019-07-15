import React from 'react';

import api from 'api';
import utils from 'utils';
import QueuedVideo from 'dataobj/queued_video';
import PlaylistItem from 'component/playlist_item';

class Playlist extends React.Component {
  constructor(props) {
    super(props);
    this.apiClient = new api();

    this.state = {
      loading: true,
      expanded: false,
      curent_video: null,
      videos: []
    };

    this.togglePlaylist = this.togglePlaylist.bind(this);
    this.nextVideo = this.nextVideo.bind(this);
    this.clearQueue = this.clearQueue.bind(this);
    this.updateStateOnLoop();
  }

  render() {
    return (
      <div className={"col-xs-12 col-md-6 playlist-container " + (this.state.expanded ? 'expanded' : '')}>
        <div className="playlist-bar">
          <div className="input-group control-input-group">
            <div className="playlist-details" onClick={this.togglePlaylist}>
              <span className="currently-playing">
                Playing: {this.getCurrentlyPlayingTitle()}
              </span>
            </div>

            <div className="input-group-btn">
              <button className="btn btn-default action-clear" type="button" onClick={this.clearQueue}>
                <span className="glyphicon glyphicon-remove-sign" aria-hidden="true" />
              </button>
              <button className="btn btn-default action-skip" type="button" onClick={this.nextVideo}>
                <span className="glyphicon glyphicon-step-forward" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>

        <div className="playlist-expand">
          <div className="playlist-contents">
              {this.state.videos.length === 0 && !this.state.loading && (
                <div class='empty'>&lt;Empty Queue&gt;</div>
              )}

              {this.state.videos.map(function(video, index) {
                return <PlaylistItem
                  key = {index}
                  video = {video} />;
              })}
          </div>
        </div>
      </div>
    );
  }

  getCurrentlyPlayingTitle() {
    if (this.state.current_video) {
      return this.state.current_video.title;
    } else if (this.state.loading) {
      return '<Loading...>';
    }

    return '<Nothing>';
  }

  togglePlaylist(e) {
    this.setState({expanded: !this.state.expanded});
  }

  clearQueue(e) {
    e.preventDefault();
    this.apiClient.clearQueue();
  }

  nextVideo(e) {
    e.preventDefault();
    this.apiClient.nextVideo();
  }

  updateStateOnLoop() {
    return this.apiClient.getQueue()
      .then((data) => {
        this.setState({ loading: false });

        if (data.success) {
          var videos = QueuedVideo.prototype.fromArray(data.queue);
          var current_video = videos.find(function(video) {
            return video.is_current;
          });

          if (current_video) {
            if ((this.state.current_video && this.state.current_video.id !== current_video.id) || !this.state.current_video) {
              this.setState({
                current_video: current_video
              });
            }
          }

          if (!utils.areArraysEqual(this.state.videos.map(video => video.id), videos.map(video => video.id))) {
            this.setState({
              videos: videos
            });
          }
        }

        setTimeout(this.updateStateOnLoop.bind(this), 5000);
      });
  }
}

export default Playlist;
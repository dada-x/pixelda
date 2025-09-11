import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import {
  GenerationService,
  FrameSplitRequest,
  FrameSplitResponse,
} from '../../services/generation.service';
import { SettingsService } from '../../services/settings.service';

@Component({
  selector: 'app-sprite-sheet',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslateModule],
  templateUrl: './sprite-sheet.component.html',
  styleUrls: ['./sprite-sheet.component.scss'],
})
export class SpriteSheetComponent implements OnInit, OnDestroy {
  videoUrl: string = '';
  fromTime: number = 0.0;
  toTime: number = 5.0;
  splitCount: number = 20;

  generatedFrames = signal<string[]>([]);

  isSplitting = signal(false);
  errorMessage = signal('');

  fromTimeError: string = '';
  toTimeError: string = '';

  selectedFrames = new Set<number>();
  showPreviewModal = signal(false);
  animationFps = 12;
  isAnimating = signal(false);
  currentFrameIndex = signal(0);
  animationInterval: any;

  showDownloadModal = signal(false);
  downloadName = '';
  isDownloading = signal(false);
  removeBackground = false;

  constructor(
    private generationService: GenerationService,
    private settingService: SettingsService
  ) {}

  ngOnInit() {
    this.loadFormData();
    const passedVideoUrl = localStorage.getItem('pixelda_sprite_sheet_video_url');
    if (passedVideoUrl) {
      this.videoUrl = passedVideoUrl;
      localStorage.removeItem('pixelda_sprite_sheet_video_url');
      this.saveFormData();
    }
  }

  ngOnDestroy() {
    this.saveFormData();
    this.stopAnimation();
  }

  private saveFormData() {
    const formData = {
      videoUrl: this.videoUrl,
      fromTime: this.fromTime,
      toTime: this.toTime,
      splitCount: this.splitCount,
    };
    localStorage.setItem('pixelda_sprite_sheet_form', JSON.stringify(formData));
  }

  private loadFormData() {
    const savedData = localStorage.getItem('pixelda_sprite_sheet_form');
    if (savedData) {
      try {
        const formData = JSON.parse(savedData);
        this.videoUrl = formData.videoUrl || '';
        this.fromTime = formData.fromTime || 0.0;
        this.toTime = formData.toTime || 10.0;
        this.splitCount = formData.splitCount || 10;
      } catch (error) {
        console.error('Error loading saved sprite sheet form data:', error);
        localStorage.removeItem('pixelda_sprite_sheet_form');
      }
    }
  }

  onFormChange() {
    this.saveFormData();
  }

  onFromTimeChange() {
    this.fromTimeError = '';
    this.toTimeError = '';

    if (this.fromTime < 0) {
      this.fromTimeError = 'SPRITE_SHEET.ERROR_FROM_TIME_NEGATIVE';
    }

    if (this.fromTime > this.toTime) {
      this.fromTimeError = 'SPRITE_SHEET.ERROR_FROM_TIME_LATER';
    }

    if (this.toTime - this.fromTime > 5) {
      this.fromTimeError = 'SPRITE_SHEET.ERROR_TIME_RANGE_EXCEEDED';
    }

    this.onFormChange();
  }

  onToTimeChange() {
    this.fromTimeError = '';
    this.toTimeError = '';

    if (this.toTime < 0) {
      this.toTimeError = 'SPRITE_SHEET.ERROR_TO_TIME_NEGATIVE';
    }

    if (this.toTime < this.fromTime) {
      this.toTimeError = 'SPRITE_SHEET.ERROR_TO_TIME_EARLIER';
    }

    if (this.toTime - this.fromTime > 5) {
      this.toTimeError = 'SPRITE_SHEET.ERROR_TIME_RANGE_EXCEEDED';
    }

    this.onFormChange();
  }

  splitVideoToFrames() {
    if (!this.videoUrl) {
      this.errorMessage.set('SPRITE_SHEET.ERROR_NO_VIDEO_URL');
      return;
    }

    if (this.fromTimeError || this.toTimeError) {
      this.errorMessage.set('SPRITE_SHEET.ERROR_FIX_TIME_INPUTS');
      return;
    }

    if (this.fromTime > this.toTime) {
      this.errorMessage.set('SPRITE_SHEET.ERROR_FROM_TIME_LATER');
      return;
    }

    if (this.toTime - this.fromTime > 5) {
      this.errorMessage.set('SPRITE_SHEET.ERROR_TIME_RANGE_EXCEEDED');
      return;
    }

    this.isSplitting.set(true);
    this.errorMessage.set('');
    this.generatedFrames.set([]);

    const request: FrameSplitRequest = {
      task_id: this.generationService.generateTaskId('frames'),
      video_url: this.videoUrl,
      from_time: this.fromTime,
      to_time: this.toTime,
      count: this.splitCount,
    };

    this.generationService.splitVideoFrames(request).subscribe({
      next: (response: FrameSplitResponse) => {
        this.isSplitting.set(false);

        if (response.frames && response.frames.length > 0) {
          this.generatedFrames.set(response.frames);
          this.selectedFrames.clear();
          this.errorMessage.set('');
        } else if (response.error_info) {
          this.errorMessage.set(response.error_info);
        } else {
          this.errorMessage.set('SPRITE_SHEET.ERROR_NO_FRAMES_GENERATED');
        }
      },
      error: (error) => {
        this.isSplitting.set(false);
        this.errorMessage.set(error.message || 'SPRITE_SHEET.ERROR_SPLIT_FAILED');
      },
    });
  }

  downloadSpriteSheet() {
    if (this.selectedFramesCount === 0) {
      this.errorMessage.set('SPRITE_SHEET.ERROR_NO_FRAMES_SELECTED');
      return;
    }

    this.downloadName = '';
    this.isDownloading.set(false);
    this.removeBackground = false;
    this.showDownloadModal.set(true);
  }

  cancelDownload() {
    this.showDownloadModal.set(false);
    this.downloadName = '';
  }

  confirmDownload() {
    if (!this.downloadName.trim()) {
      return;
    }

    this.isDownloading.set(true);
    this.errorMessage.set('');

    const selectedFrameUrls = this.getSelectedFrames();
    const request = {
      name: this.downloadName.trim(),
      frame_urls: selectedFrameUrls,
      removebg: this.removeBackground,
    };

    this.generationService.zipFrames(request).subscribe({
      next: (blob: Blob) => {
        this.isDownloading.set(false);
        this.showDownloadModal.set(false);

        this.downloadName = '';
        this.removeBackground = false;

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${request.name}_frames.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        this.errorMessage.set('');
      },
      error: (error) => {
        this.isDownloading.set(false);
        this.errorMessage.set(error.message || 'SPRITE_SHEET.ERROR_DOWNLOAD_FAILED');
        console.error('Download error:', error);
      },
    });
  }

  toggleFrameSelection(frameIndex: number) {
    if (this.selectedFrames.has(frameIndex)) {
      this.selectedFrames.delete(frameIndex);
    } else {
      this.selectedFrames.add(frameIndex);
    }
  }

  isFrameSelected(frameIndex: number): boolean {
    return this.selectedFrames.has(frameIndex);
  }

  selectAllFrames() {
    const frames = this.generatedFrames();
    for (let i = 0; i < frames.length; i++) {
      this.selectedFrames.add(i);
    }
  }

  deselectAllFrames() {
    this.selectedFrames.clear();
  }

  getSelectedFrames(): string[] {
    const frames = this.generatedFrames();

    const selectedFrameUrls = Array.from(this.selectedFrames)
      .map((index) => frames[index])
      .filter((frame) => frame);

    return selectedFrameUrls;
  }

  get selectedFramesCount(): number {
    return this.getSelectedFrames().length;
  }

  openPreviewModal() {
    if (this.selectedFramesCount === 0) {
      this.errorMessage.set('SPRITE_SHEET.ERROR_NO_FRAMES_PREVIEW');
      return;
    }
    this.showPreviewModal.set(true);
    this.currentFrameIndex.set(0);
    this.isAnimating.set(false);
    this.stopAnimation();
  }

  closePreviewModal() {
    this.showPreviewModal.set(false);
    this.stopAnimation();
  }

  startAnimation() {
    if (this.selectedFramesCount === 0) {
      return;
    }

    if (this.currentFrameIndex() >= this.selectedFramesCount) {
      this.currentFrameIndex.set(0);
    }

    this.isAnimating.set(true);
    const interval = 1000 / this.animationFps;
    const selectedFramesCount = this.selectedFramesCount;

    this.animationInterval = setInterval(() => {
      this.currentFrameIndex.set((this.currentFrameIndex() + 1) % selectedFramesCount);
    }, interval);
  }

  stopAnimation() {
    this.isAnimating.set(false);
    if (this.animationInterval) {
      clearInterval(this.animationInterval);
      this.animationInterval = null;
    }
    this.currentFrameIndex.set(0);
  }

  toggleAnimation() {
    if (this.isAnimating()) {
      this.stopAnimation();
    } else {
      this.startAnimation();
    }
  }

  getCurrentAnimationFrame(): string {
    const selectedFrames = this.getSelectedFrames();

    if (selectedFrames.length === 0) {
      return '';
    }

    if (this.currentFrameIndex() >= selectedFrames.length) {
      this.currentFrameIndex.set(0);
    }

    const frameUrl = selectedFrames[this.currentFrameIndex()];

    if (!frameUrl) {
      return '';
    }

    return frameUrl;
  }

  setAnimationFps(fps: number) {
    this.animationFps = fps;
    if (this.isAnimating()) {
      this.stopAnimation();
      this.startAnimation();
    }
  }
}

import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import 'media-chrome';
import {
  GenerationService,
  MusicGenerationRequest,
  MusicResponse,
} from '../../services/generation.service';
import { SettingsService } from '../../services/settings.service';

@Component({
  selector: 'app-music',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslateModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './music.component.html',
  styleUrls: ['./music.component.scss'],
})
export class MusicComponent implements OnInit, OnDestroy {
  prompt = '';
  duration = 30;
  genre = 'pop';
  tempo = 'moderato';
  seed: number | null = null;

  result = signal<MusicResponse | null>(null);
  loading = signal(false);
  audioLoading = signal(false);

  constructor(
    private generationService: GenerationService,
    private settingService: SettingsService,
    private translate: TranslateService
  ) {}

  ngOnInit() {
    this.loadFormData();
  }

  ngOnDestroy() {
    this.saveFormData();
  }

  private saveFormData() {
    const formData = {
      prompt: this.prompt,
      duration: this.duration,
      genre: this.genre,
      tempo: this.tempo,
      seed: this.seed,
    };
    localStorage.setItem('pixelda_music_form', JSON.stringify(formData));
  }

  private loadFormData() {
    const savedData = localStorage.getItem('pixelda_music_form');
    if (savedData) {
      try {
        const formData = JSON.parse(savedData);
        this.prompt = formData.prompt || '';
        this.duration = formData.duration || 30;
        this.genre = formData.genre || 'pop';
        this.tempo = formData.tempo || 'moderato';
        this.seed = formData.seed;
      } catch (error) {
        console.error('Error loading saved form data:', error);
        localStorage.removeItem('pixelda_music_form');
      }
    }
  }

  onFormChange() {
    this.saveFormData();
  }

  generateMusic() {
    const prompt = this.prompt.trim();
    if (!prompt) {
      alert('Please provide a music description');
      return;
    }

    this.loading.set(true);
    this.audioLoading.set(true);

    const request: MusicGenerationRequest = {
      prompt,
      duration: this.duration,
      genre: this.genre,
      tempo: this.tempo,
      seed: this.seed || undefined,
      task_id: this.generationService.generateTaskId('music'),
      model_type: this.settingService.getActiveModel(),
    };

    this.generationService.generateMusic(request).subscribe({
      next: (result) => {
        this.result.set(result);
        this.loading.set(false);
        if ((result.original || result.chiptune) && !result.error_info) {
          this.storeGenerationToHistory(result, prompt);
        }
      },
      error: (error) => {
        this.result.set({
          original: '',
          chiptune: '',
          task_id: request.task_id,
          error_info: error.message,
        });
        this.loading.set(false);
        this.audioLoading.set(false);
      },
    });
  }

  clearForm() {
    this.prompt = '';
    this.duration = 30;
    this.genre = 'pop';
    this.tempo = 'moderato';
    this.seed = null;
    this.result.set(null);
    localStorage.removeItem('pixelda_music_form');
  }

  regenerateMusic() {
    if (this.result() && !this.result()!.error_info) {
      this.generateMusic();
    }
  }

  onAudioLoad() {
    this.audioLoading.set(false);
  }

  onAudioError() {
    this.audioLoading.set(false);
    console.error('Failed to load generated audio');
  }

  async downloadFile(url: string, filename: string) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setTimeout(() => {
        window.URL.revokeObjectURL(downloadUrl);
      }, 100);
    } catch (error) {
      console.error('Download failed:', error);
      window.open(url, '_blank');
    }
  }

  downloadOriginal() {
    if (this.result()?.original) {
      const filename = this.extractFilename(this.result()!.original) || 'original.wav';
      this.downloadFile(this.result()!.original, filename);
    }
  }

  downloadChiptune() {
    if (this.result()?.chiptune) {
      const filename = this.extractFilename(this.result()!.chiptune) || 'chiptune.wav';
      this.downloadFile(this.result()!.chiptune, filename);
    }
  }

  private extractFilename(url: string): string | null {
    try {
      const urlObj = new URL(url);
      const pathname = urlObj.pathname;
      const filename = pathname.split('/').pop();
      return filename || null;
    } catch (error) {
      const parts = url.split('/');
      return parts[parts.length - 1] || null;
    }
  }

  private storeGenerationToHistory(result: MusicResponse, prompt: string) {
    const historyItem = {
      id: result.task_id || `music_${Date.now()}`,
      type: 'music',
      original: result.original,
      chiptune: result.chiptune,
      prompt: prompt,
      timestamp: new Date().toISOString(),
      duration: this.duration,
      genre: this.genre,
      tempo: this.tempo,
      seed: this.seed,
    };

    const existingHistory = localStorage.getItem('pixelda_generation_history');
    let history: any[] = [];

    if (existingHistory) {
      try {
        history = JSON.parse(existingHistory);
      } catch (error) {
        console.error('Error parsing generation history:', error);
        history = [];
      }
    }

    const now = new Date();
    const maxAge = 24 * 60 * 60 * 1000;
    history = history.filter((item) => {
      const itemDate = new Date(item.timestamp);
      const age = now.getTime() - itemDate.getTime();
      return age <= maxAge;
    });

    history.unshift(historyItem);

    if (history.length > 50) {
      history = history.slice(0, 50);
    }

    localStorage.setItem('pixelda_generation_history', JSON.stringify(history));
  }
}

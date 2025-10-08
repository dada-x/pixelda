import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import {
  GenerationService,
  VideoGenerationRequest,
  GenerationResponse,
} from '../../services/generation.service';
import { SettingsService } from '../../services/settings.service';

@Component({
  selector: 'app-animation',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslateModule],
  templateUrl: './animation.component.html',
  styleUrls: ['./animation.component.scss'],
})
export class AnimationComponent implements OnInit, OnDestroy {
  imageUrl = signal('');
  prompt: string = '';
  negativePrompt: string = '';
  resolution: string = '480P';

  isLocalImage = signal(false);
  displayImageUrl = signal('');
  fileName = signal('');

  result = signal<GenerationResponse | null>(null);

  isGenerating = signal(false);
  errorMessage = signal('');

  constructor(
    private generationService: GenerationService,
    private settingService: SettingsService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadFormData();
    const passedImageUrl = localStorage.getItem('pixelda_animation_image_url');
    if (passedImageUrl) {
      this.imageUrl.set(passedImageUrl);
      localStorage.removeItem('pixelda_animation_image_url');
      this.isLocalImage.set(this.imageUrl().startsWith('data:'));
      this.displayImageUrl.set(this.isLocalImage() ? this.fileName() || 'local image' : this.imageUrl());
      this.saveFormData();
    }
  }

  ngOnDestroy() {
    this.saveFormData();
  }

  private saveFormData() {
    const formData = {
      imageUrl: this.imageUrl(),
      prompt: this.prompt,
      negativePrompt: this.negativePrompt,
      resolution: this.resolution,
      fileName: this.fileName(),
    };
    localStorage.setItem('pixelda_animation_form', JSON.stringify(formData));
  }

  private loadFormData() {
    const savedData = localStorage.getItem('pixelda_animation_form');
    if (savedData) {
      try {
        const formData = JSON.parse(savedData);
        this.imageUrl.set(formData.imageUrl || '');
        this.prompt = formData.prompt || '';
        this.negativePrompt = formData.negativePrompt || '';
        this.resolution = formData.resolution || '480P';
        this.fileName.set(formData.fileName || '');
        this.isLocalImage.set(this.imageUrl().startsWith('data:'));
        this.displayImageUrl.set(this.isLocalImage() ? this.fileName() : this.imageUrl());
      } catch (error) {
        console.error('Error loading saved animation form data:', error);
        localStorage.removeItem('pixelda_animation_form');
      }
    }
  }

  onFormChange() {
    if (this.displayImageUrl() !== this.fileName()) {
      this.isLocalImage.set(false);
    }
    if (!this.isLocalImage()) {
      this.imageUrl.set(this.displayImageUrl());
    }
    this.saveFormData();
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file && (file.type === 'image/png' || file.type === 'image/jpeg')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imageUrl.set(e.target?.result as string);
        this.displayImageUrl.set(file.name);
        this.fileName.set(file.name);
        this.isLocalImage.set(true);
        this.onFormChange();
      };
      reader.readAsDataURL(file);
    }
    event.target.value = '';
  }

  triggerFileInput() {
    const fileInput = document.getElementById('fileInput') as HTMLInputElement;
    fileInput.click();
  }

  generateAnimation() {
    if (!this.imageUrl() || !this.prompt) {
      this.errorMessage.set('Please provide both image URL and prompt');
      return;
    }

    this.isGenerating.set(true);
    this.errorMessage.set('');
    this.result.set(null);

    const request: VideoGenerationRequest = {
      base_image_url: this.imageUrl(),
      prompt: 'pixel-art game animation, ' + this.prompt,
      negative_prompt: this.negativePrompt || undefined,
      resolution: this.resolution,
      task_id: this.generationService.generateTaskId('anim'),
      model_type: this.settingService.getActiveModel(),
    };

    this.generationService.generateVideo(request).subscribe({
      next: (response: GenerationResponse) => {
        this.isGenerating.set(false);
        if (response.url) {
          this.result.set(response);
          this.storeGenerationToHistory(response, request.prompt);
        } else if (response.error_info) {
          this.errorMessage.set(response.error_info);
        }
      },
      error: (error) => {
        this.isGenerating.set(false);
        this.errorMessage.set(error.message || 'Failed to generate animation');
      },
    });
  }

  private storeGenerationToHistory(result: GenerationResponse, prompt: string) {
    const historyItem = {
      id: result.task_id || `anim_${Date.now()}`,
      type: 'animation',
      url: result.url,
      prompt: prompt,
      baseImageUrl: this.imageUrl(),
      timestamp: new Date().toISOString(),
      resolution: this.resolution,
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

  reset() {
    this.imageUrl.set('');
    this.prompt = '';
    this.negativePrompt = '';
    this.resolution = '480P';
    this.isLocalImage.set(false);
    this.displayImageUrl.set('');
    this.fileName.set('');
    this.result.set(null);
    this.errorMessage.set('');
    localStorage.removeItem('pixelda_animation_form');
  }

  navigateToSpriteSheet() {
    if (this.result() && this.result()!.url) {
      localStorage.setItem('pixelda_sprite_sheet_video_url', this.result()!.url);
      this.router.navigate(['/generate/sprite-sheet']);
    }
  }

  onThumbnailError() {}
}

import { Component, OnInit, ViewChildren, QueryList, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { AlertService } from '../../services/alert.service';
import { AlertModalComponent } from './alert-modal.component';

interface GenerationHistoryItem {
  id: string;
  type: string;
  url: string;
  prompt: string;
  timestamp: string;
  size?: string;
  seed?: number;
  resolution?: string;
  baseImageUrl?: string;
}

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, TranslateModule, AlertModalComponent],
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.scss'],
})
export class HistoryComponent implements OnInit {
  historyItems: GenerationHistoryItem[] = [];
  private readonly MAX_AGE_HOURS = 24;
  hoveredItem: GenerationHistoryItem | null = null;
  previewVisible: boolean = false;
  previewLeft: number = 0;
  previewTop: number = 0;

  @ViewChildren('itemImage') itemImages!: QueryList<ElementRef>;

  constructor(public alertService: AlertService) {}

  ngOnInit() {
    this.loadGenerationHistory();
  }

  loadGenerationHistory() {
    const storedHistory = localStorage.getItem('pixelda_generation_history');
    if (storedHistory) {
      try {
        this.historyItems = JSON.parse(storedHistory);
        this.cleanupOldRecords();
      } catch (error) {
        console.error('Error parsing generation history:', error);
        this.historyItems = [];
      }
    } else {
      this.historyItems = [];
    }
  }

  private cleanupOldRecords() {
    const now = new Date();
    const maxAge = this.MAX_AGE_HOURS * 60 * 60 * 1000;

    const originalCount = this.historyItems.length;
    this.historyItems = this.historyItems.filter((item) => {
      const itemDate = new Date(item.timestamp);
      const age = now.getTime() - itemDate.getTime();
      return age <= maxAge;
    });

    const removedCount = originalCount - this.historyItems.length;
    if (removedCount > 0) {
      localStorage.setItem('pixelda_generation_history', JSON.stringify(this.historyItems));
    }
  }

  formatDate(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleString();
  }

  getPreviewUrl(item: GenerationHistoryItem): string | null {
    if (item.type === 'animation' && item.baseImageUrl) {
      return item.baseImageUrl;
    }
    return item.url || null;
  }

  getCopyUrl(item: GenerationHistoryItem): string | null {
    return item.url || null;
  }

  clearHistory() {
    this.alertService.showConfirmWithKeys(
      'HISTORY.CLEAR_ALL',
      'HISTORY.CLEAR_ALL_CONFIRM',
      () => {
        localStorage.removeItem('pixelda_generation_history');
        this.historyItems = [];
      },
      undefined,
      'HISTORY.CLEAR_ALL',
      'ALERTS.CANCEL'
    );
  }

  removeHistoryItem(itemId: string) {
    this.historyItems = this.historyItems.filter((item) => item.id !== itemId);
    localStorage.setItem('pixelda_generation_history', JSON.stringify(this.historyItems));
  }

  onMouseEnter(item: GenerationHistoryItem) {
    this.hoveredItem = item;
    const index = this.historyItems.indexOf(item);
    const itemImageArray = this.itemImages.toArray();
    if (itemImageArray[index]) {
      const rect = itemImageArray[index].nativeElement.getBoundingClientRect();
      this.previewLeft = rect.left + 100;
      this.previewTop = rect.top - 10;
      this.previewVisible = true;
    }
  }

  onMouseLeave() {
    this.hoveredItem = null;
    this.previewVisible = false;
  }
  async copyUrl(url: string | null, event?: Event) {
    if (!url) {
      return;
    }

    const button = event?.target as HTMLElement;
    if (button) {
      button.classList.add('copied');
      setTimeout(() => {
        button.classList.remove('copied');
      }, 600);
    }

    try {
      await navigator.clipboard.writeText(url);
    } catch (error) {
      console.error('Failed to copy URL:', error);

      const textArea = document.createElement('textarea');
      textArea.value = url;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
      } catch (fallbackError) {
        console.error('Fallback copy failed:', fallbackError);
      }
      document.body.removeChild(textArea);
    }
  }
}

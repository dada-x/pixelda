import { Component, signal, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { AlertConfig } from '../../services/alert.service';

@Component({
  selector: 'app-alert-modal',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  template: `
    <div class="alert-overlay" (click)="onOverlayClick()">
      <div class="alert-modal" (click)="$event.stopPropagation()">
        <div class="alert-header">
          <h3 class="alert-title">
            {{ config().titleKey ? (config().titleKey | translate) : config().title }}
          </h3>
          <button class="alert-close" (click)="onClose()">×</button>
        </div>
        <div class="alert-body">
          <p class="alert-message">
            {{ config().messageKey ? (config().messageKey | translate) : config().message }}
          </p>
        </div>
        <div class="alert-footer" *ngIf="config().type === 'confirm'">
          <button class="alert-btn alert-cancel" (click)="onCancel()">
            {{
              config().cancelTextKey
                ? (config().cancelTextKey | translate)
                : config().cancelText || 'Cancel'
            }}
          </button>
          <button class="alert-btn alert-confirm" (click)="onConfirm()">
            {{
              config().confirmTextKey
                ? (config().confirmTextKey | translate)
                : config().confirmText || 'Confirm'
            }}
          </button>
        </div>
        <div class="alert-footer" *ngIf="config().type !== 'confirm'">
          <button class="alert-btn alert-ok" (click)="onClose()">OK</button>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./alert-modal.component.scss'],
})
export class AlertModalComponent {
  config = input.required<AlertConfig>();
  confirm = output<void>();
  cancel = output<void>();
  close = output<void>();

  onConfirm() {
    this.confirm.emit();
  }

  onCancel() {
    this.cancel.emit();
  }

  onClose() {
    this.close.emit();
  }

  onOverlayClick() {
    this.close.emit();
  }
}

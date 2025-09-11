import { Injectable, signal } from '@angular/core';

export interface AlertConfig {
  title: string;
  message: string;
  type: 'success' | 'error' | 'confirm';
  confirmText?: string;
  cancelText?: string;
  titleKey?: string;
  messageKey?: string;
  confirmTextKey?: string;
  cancelTextKey?: string;
}

@Injectable({
  providedIn: 'root',
})
export class AlertService {
  private showAlertSignal = signal(false);
  private alertConfigSignal = signal<AlertConfig | null>(null);

  readonly showAlert = this.showAlertSignal.asReadonly();
  readonly alertConfig = this.alertConfigSignal.asReadonly();

  showSuccess(title: string, message: string) {
    this.showAlertSignal.set(true);
    this.alertConfigSignal.set({
      title,
      message,
      type: 'success',
    });
  }

  showSuccessWithKeys(titleKey: string, messageKey: string) {
    this.showAlertSignal.set(true);
    this.alertConfigSignal.set({
      title: '',
      message: '',
      type: 'success',
      titleKey,
      messageKey,
    });
  }

  showError(title: string, message: string) {
    this.showAlertSignal.set(true);
    this.alertConfigSignal.set({
      title,
      message,
      type: 'error',
    });
  }

  showErrorWithKeys(titleKey: string, messageKey: string) {
    this.showAlertSignal.set(true);
    this.alertConfigSignal.set({
      title: '',
      message: '',
      type: 'error',
      titleKey,
      messageKey,
    });
  }

  showConfirm(
    title: string,
    message: string,
    onConfirm: () => void,
    onCancel?: () => void,
    confirmText = 'Confirm',
    cancelText = 'Cancel'
  ) {
    this.showAlertSignal.set(true);
    this.alertConfigSignal.set({
      title,
      message,
      type: 'confirm',
      confirmText,
      cancelText,
    });

    this.pendingConfirmCallback = onConfirm;
    this.pendingCancelCallback = onCancel;
  }

  showConfirmWithKeys(
    titleKey: string,
    messageKey: string,
    onConfirm: () => void,
    onCancel?: () => void,
    confirmTextKey = 'ALERTS.CONFIRM',
    cancelTextKey = 'ALERTS.CANCEL'
  ) {
    this.showAlertSignal.set(true);
    this.alertConfigSignal.set({
      title: '',
      message: '',
      type: 'confirm',
      confirmText: '',
      cancelText: '',
      titleKey,
      messageKey,
      confirmTextKey,
      cancelTextKey,
    });

    this.pendingConfirmCallback = onConfirm;
    this.pendingCancelCallback = onCancel;
  }

  hideAlert() {
    this.showAlertSignal.set(false);
    this.alertConfigSignal.set(null);
    this.clearPendingCallbacks();
  }

  onConfirm() {
    if (this.pendingConfirmCallback) {
      this.pendingConfirmCallback();
    }
    this.hideAlert();
  }

  onCancel() {
    if (this.pendingCancelCallback) {
      this.pendingCancelCallback();
    }
    this.hideAlert();
  }

  onClose() {
    this.hideAlert();
  }

  private pendingConfirmCallback?: () => void;
  private pendingCancelCallback?: () => void;

  private clearPendingCallbacks() {
    this.pendingConfirmCallback = undefined;
    this.pendingCancelCallback = undefined;
  }
}

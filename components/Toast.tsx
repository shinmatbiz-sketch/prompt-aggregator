"use client";

import { useEffect, useState } from "react";
import { Check } from "lucide-react";

interface ToastProps {
  message: string;
  visible: boolean;
  onClose: () => void;
}

export default function Toast({ message, visible, onClose }: ToastProps) {
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    if (!visible) return;

    const timer = setTimeout(() => {
      setExiting(true);
      setTimeout(onClose, 150);
    }, 2000);

    return () => clearTimeout(timer);
  }, [visible, onClose]);

  useEffect(() => {
    if (visible) setExiting(false);
  }, [visible]);

  if (!visible) return null;

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
      <div
        className={`flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg shadow-lg ${
          exiting ? "toast-exit" : "toast-enter"
        }`}
      >
        <Check className="w-4 h-4 text-emerald-400" />
        {message}
      </div>
    </div>
  );
}

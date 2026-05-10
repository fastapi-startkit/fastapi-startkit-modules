import React, { useState, useRef, useEffect, ComponentProps } from 'react';
import { fileSize } from '@/utils';
import { Omit } from 'lodash';

interface FileInputProps extends Omit<ComponentProps<'input'>, 'onChange'> {
  error?: string;
  /** Existing image URL to show as a preview (e.g. from the server) */
  existingPhotoUrl?: string | null;
  onChange?: (file: File | null) => void;
}

export default function FileInput({ name, error, onChange, existingPhotoUrl }: FileInputProps) {
  const fileInput = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(existingPhotoUrl ?? null);

  // Revoke the object URL when the component unmounts to avoid memory leaks
  useEffect(() => {
    return () => {
      if (preview && preview.startsWith('blob:')) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  function handleBrowse() {
    fileInput?.current?.click();
  }

  function handleRemove() {
    setFile(null);
    setPreview(existingPhotoUrl ?? null);
    onChange?.(null);
  }

  function handleChange(e: React.FormEvent<HTMLInputElement>) {
    const files = e.currentTarget?.files as FileList;
    const selected = files[0] || null;

    setFile(selected);
    onChange?.(selected);

    if (selected && selected.type.startsWith('image/')) {
      const objectUrl = URL.createObjectURL(selected);
      setPreview(objectUrl);
    } else {
      setPreview(existingPhotoUrl ?? null);
    }
  }

  return (
    <div
      className={`form-input w-full focus:outline-none focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 border-gray-300 rounded p-0 ${
        error && 'border-red-400 focus:border-red-400 focus:ring-red-400'
      }`}
    >
      <input
        id={name}
        ref={fileInput}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleChange}
      />

      {/* Image preview */}
      {preview && (
        <div className="flex justify-center pt-3 pb-1">
          <img
            src={preview}
            alt="Profile preview"
            className="w-20 h-20 rounded-full object-cover ring-2 ring-indigo-300 shadow"
          />
        </div>
      )}

      {!file && (
        <div className="p-2">
          <BrowseButton text={preview ? 'Change photo' : 'Browse'} onClick={handleBrowse} />
        </div>
      )}
      {file && (
        <div className="flex items-center justify-between p-2">
          <div className="flex-1 pr-1 text-sm truncate">
            {file?.name}
            <span className="ml-1 text-xs text-gray-600">
              ({fileSize(file?.size)})
            </span>
          </div>
          <div className="flex gap-1">
            <BrowseButton text="Change" onClick={handleBrowse} />
            <BrowseButton text="Remove" onClick={handleRemove} />
          </div>
        </div>
      )}
    </div>
  );
}

interface BrowseButtonProps extends ComponentProps<'button'> {
  text: string;
}

function BrowseButton({ text, onClick, ...props }: BrowseButtonProps) {
  return (
    <button
      {...props}
      type="button"
      className="px-4 py-1 text-xs font-medium text-white bg-gray-600 rounded-sm focus:outline-none hover:bg-gray-700"
      onClick={onClick}
    >
      {text}
    </button>
  );
}

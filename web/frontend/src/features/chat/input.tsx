import React from 'react';
import { TextField } from '@mui/material';

interface InputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSend: () => void;
}

export function Input({ value, onChange, onSend }: InputProps) {
  return (
    <TextField
      fullWidth
      multiline
      rows={2}
      variant="outlined"
      value={value}
      onChange={onChange}
      placeholder="输入任务，例如：写一段小说大纲…"
      onKeyDown={(e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          onSend();
        }
      }}
      sx={{
        backgroundColor: '#1e1e1e',
        borderRadius: 1,
        '& .MuiInputBase-input': {
          color: 'white',
        },
        '& .MuiOutlinedInput-notchedOutline': {
          borderColor: 'transparent',
        },
        '&:hover .MuiOutlinedInput-notchedOutline': {
          borderColor: 'transparent',
        },
      }}
    />
  );
}

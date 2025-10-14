import React, { useState } from 'react';
import { PromptCard } from '../components/PromptCard';
import { Prompt } from '../types';

const HomePage: React.FC = () => {
  const [prompts, setPrompts] = useState<Prompt[]>([
    {
      id: '1',
      title: 'Creative Writing Assistant',
      content: 'Write a creative story about {topic} in the style of {author} for {audience}.',
      category: 'Creative Writing',
      tags: ['story', 'creative', 'writing'],
      createdAt: new Date(),
      updatedAt: new Date(),
      isTemplate: true,
      variables: ['topic', 'author', 'audience'],
      usageCount: 15,
      rating: 4.5,
    },
    {
      id: '2',
      title: 'Code Review Helper',
      content: 'Please review this {language} code and provide suggestions for improvement: {code}',
      category: 'Programming',
      tags: ['code', 'review', 'programming'],
      createdAt: new Date(),
      updatedAt: new Date(),
      isTemplate: true,
      variables: ['language', 'code'],
      usageCount: 8,
      rating: 4.2,
    },
  ]);

  const handleEdit = (prompt: Prompt) => {
    console.log('Edit prompt:', prompt);
    // TODO: Implement edit functionality
  };

  const handleDelete = (promptId: string) => {
    setPrompts(prompts.filter(p => p.id !== promptId));
  };

  const handleDuplicate = (prompt: Prompt) => {
    const newPrompt = {
      ...prompt,
      id: Date.now().toString(),
      title: `${prompt.title} (Copy)`,
      createdAt: new Date(),
      updatedAt: new Date(),
      usageCount: 0,
    };
    setPrompts([...prompts, newPrompt]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI Prompt Tool</h1>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            New Prompt
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {prompts.map((prompt) => (
            <PromptCard
              key={prompt.id}
              prompt={prompt}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onDuplicate={handleDuplicate}
            />
          ))}
        </div>

        {prompts.length === 0 && (
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-gray-600 mb-4">
              No prompts yet
            </h2>
            <p className="text-gray-500 mb-6">
              Create your first AI prompt to get started
            </p>
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
              Create Your First Prompt
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;

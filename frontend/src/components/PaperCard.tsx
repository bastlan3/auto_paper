import React from 'react';

interface Paper {
  id: string;
  title: string;
  authors: string[];
  publishedDate: string;
  category: string;
  summary: string;
}

interface PaperCardProps {
  paper: Paper;
}

const PaperCard: React.FC<PaperCardProps> = ({ paper }) => {
  const displayAuthors = paper.authors.slice(0, 3);
  const hasMoreAuthors = paper.authors.length > 3;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 h-full flex flex-col shadow-sm hover:shadow-lg transition-shadow duration-300">
      <h2 className="text-lg font-bold font-sans text-text-primary mb-2">
        {paper.title}
      </h2>
      <div className="text-sm text-text-secondary italic mb-3 group relative">
        {displayAuthors.join(', ')}
        {hasMoreAuthors && (
          <>
            , <span className="cursor-pointer">et al.</span>
            <div className="absolute bottom-full mb-2 w-auto max-w-xs bg-gray-800 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10 p-2 break-words">
              {paper.authors.join(', ')}
            </div>
          </>
        )}
      </div>
      <div className="text-xs text-text-secondary mb-4">
        <span>Published: {paper.publishedDate}</span>
        <span className="mx-2">|</span>
        <span>Category: {paper.category}</span>
      </div>
      <p className="text-base font-serif text-text-primary leading-relaxed flex-grow">
        {paper.summary}
      </p>
    </div>
  );
};

export default PaperCard;
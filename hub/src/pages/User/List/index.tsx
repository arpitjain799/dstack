import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Button,
    Table,
    Header,
    Pagination,
    SpaceBetween,
    TextFilter,
    NavigateLink,
    ListEmptyMessage,
    ConfirmationDialog,
} from 'components';
import { useDeleteUsersMutation, useGetUserListQuery } from 'services/user';
import { useBreadcrumbs, useCollection } from 'hooks';
import { ROUTES } from 'routes';
import { useTranslation } from 'react-i18next';

export const UserList: React.FC = () => {
    const { t } = useTranslation();
    const [showDeleteConfirm, setShowConfirmDelete] = useState(false);
    const { isLoading, data } = useGetUserListQuery();
    const [deleteUsers, { isLoading: isDeleting }] = useDeleteUsersMutation();
    const navigate = useNavigate();

    useBreadcrumbs([
        {
            text: t('navigation.users'),
            href: ROUTES.USER.LIST,
        },
    ]);

    const COLUMN_DEFINITIONS = [
        {
            id: 'name',
            header: t('users.user_name'),
            cell: (item: IUser) => (
                <NavigateLink href={ROUTES.USER.DETAILS.FORMAT(item.user_name)}>{item.user_name}</NavigateLink>
            ),
        },
        {
            id: 'global_role',
            header: t('users.global_role'),
            cell: (item: IUser) => t(`roles.${item.global_role}`),
        },
    ];

    const toggleDeleteConfirm = () => {
        setShowConfirmDelete((val) => !val);
    };

    const renderEmptyMessage = (): React.ReactNode => {
        return <ListEmptyMessage title={t('users.empty_message_title')} message={t('hubs.empty_message_text')} />;
    };

    const renderNoMatchMessage = (onClearFilter: () => void): React.ReactNode => {
        return (
            <ListEmptyMessage title={t('users.nomatch_message_title')} message={t('users.nomatch_message_text')}>
                <Button onClick={onClearFilter}>{t('users.nomatch_message_button_label')}</Button>
            </ListEmptyMessage>
        );
    };

    const { items, actions, filteredItemsCount, collectionProps, filterProps, paginationProps } = useCollection(data ?? [], {
        filtering: {
            empty: renderEmptyMessage(),
            noMatch: renderNoMatchMessage(() => actions.setFiltering('')),
        },
        pagination: { pageSize: 20 },
        selection: {},
    });

    useEffect(() => {
        if (!isDeleting) actions.setSelectedItems([]);
    }, [isDeleting]);

    const deleteSelectedUserHandler = () => {
        const { selectedItems } = collectionProps;
        if (selectedItems?.length) deleteUsers(selectedItems.map((user) => user.user_name));
        setShowConfirmDelete(false);
    };

    const addUserHandler = () => {
        navigate(ROUTES.USER.ADD);
    };

    const editSelectedUserHandler = () => {
        const { selectedItems } = collectionProps;

        if (selectedItems?.length) navigate(ROUTES.USER.DETAILS.FORMAT(selectedItems[0].user_name));
    };

    const getIsTableItemDisabled = () => {
        return isDeleting;
    };

    const isDisabledDelete = useMemo(() => {
        return isDeleting || collectionProps.selectedItems?.length === 0;
    }, [collectionProps.selectedItems]);

    const isDisabledEdit = useMemo(() => {
        return isDeleting || collectionProps.selectedItems?.length !== 1;
    }, [collectionProps.selectedItems]);

    const renderCounter = () => {
        const { selectedItems } = collectionProps;

        if (!data?.length) return '';

        if (selectedItems?.length) return `(${selectedItems?.length}/${data?.length ?? 0})`;

        return `(${data.length})`;
    };

    return (
        <>
            <Table
                {...collectionProps}
                variant="full-page"
                isItemDisabled={getIsTableItemDisabled}
                columnDefinitions={COLUMN_DEFINITIONS}
                items={items}
                loading={isLoading}
                loadingText={t('common.loading')}
                selectionType="multi"
                stickyHeader={true}
                header={
                    <Header
                        variant="awsui-h1-sticky"
                        counter={renderCounter()}
                        actions={
                            <SpaceBetween size="xs" direction="horizontal">
                                <Button formAction="none" onClick={editSelectedUserHandler} disabled={isDisabledEdit}>
                                    {t('common.edit')}
                                </Button>

                                <Button formAction="none" onClick={toggleDeleteConfirm} disabled={isDisabledDelete}>
                                    {t('common.delete')}
                                </Button>

                                <Button formAction="none" onClick={addUserHandler}>
                                    {t('common.add')}
                                </Button>
                            </SpaceBetween>
                        }
                    >
                        {t('users.page_title')}
                    </Header>
                }
                filter={
                    <TextFilter
                        {...filterProps}
                        filteringPlaceholder={t('users.search_placeholder')}
                        countText={t('common.match_count_with_value', { count: filteredItemsCount })}
                        disabled={isLoading}
                    />
                }
                pagination={<Pagination {...paginationProps} disabled={isLoading} />}
            />

            <ConfirmationDialog
                visible={showDeleteConfirm}
                onDiscard={toggleDeleteConfirm}
                onConfirm={deleteSelectedUserHandler}
            />
        </>
    );
};
